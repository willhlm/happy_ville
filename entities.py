import pygame, random, sys, math
import read_files, particles, animation, dialogue, states, groups
import states_exploding_mygga, states_droplets, states_twoD_liquid, states_death, states_lever, states_blur, states_grind, states_portal, states_froggy, states_sword, states_fireplace, states_shader_guide, states_shader, states_butterfly, states_cocoon_boss, states_maggot, states_horn_vines, states_basic, states_camerastop, states_player, states_traps, states_NPC, states_enemy, states_vatt, states_enemy_flying, states_reindeer, states_bird, states_kusa, states_rogue_cultist, states_sandrew
import AI_froggy, AI_butterfly, AI_maggot, AI_wall_slime, AI_vatt, AI_kusa, AI_enemy_flying, AI_bird, AI_enemy, AI_reindeer, AI_mygga
import constants as C

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class Staticentity(pygame.sprite.Sprite):#all enteties
    def __init__(self, pos, game_objects):
        super().__init__()
        self.game_objects = game_objects
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)
        self.true_pos = list(self.rect.topleft)

        self.bounds = [-200, 800, -100, 350]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.parallax = [1,1]
        self.shader = None#which shader program to run
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: needed when rendering the direction

    def group_distance(self):
        blit_pos = [self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.true_pos[1]-self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        if blit_pos[0] < self.bounds[0] or blit_pos[0] > self.bounds[1] or blit_pos[1] < self.bounds[2] or blit_pos[1] > self.bounds[3]:
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause

    def draw(self, target):#called just before draw in group
        pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, flip = bool(max(self.dir[0],0)), shader = self.shader)#shader render

    def kill(self):
        self.release_texture()#before killing, need to release the textures (but not the onces who has a pool)
        super().kill()

class BG_Block(Staticentity):
    def __init__(self, pos, game_objects, img, parallax, live_blur = False):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.layers = None  # Initialize layer to None
        self.image = self.game_objects.game.display.surface_to_texture(img)
        self.rect[2] = self.image.width
        self.rect[3] = self.image.height

        self.blur_radius = min(1/self.parallax[0], 10)#set a limit to 10. Bigger may cause performance issue

        if not live_blur:
            self.blurstate = states_blur.Idle(self)
            self.blur()#if we do not want live blur
        else:#if live
            self.blurstate = states_blur.Blur(self)
            if self.parallax[0] == 1: self.blur_radius = 0.2#a small value so you don't see blur

    def blur(self):
        if self.parallax[0] != 1:  # Don't blur if there is no parallax
            shader = self.game_objects.shaders['blur']
            shader['blurRadius'] = self.blur_radius  # Set the blur radius
            self.game_objects.game.display.use_alpha_blending(False)#remove thr black outline
            self.layers = self.game_objects.game.display.make_layer(self.image.size)# Make an empty layer
            self.game_objects.game.display.render(self.image, self.layers, shader = shader)  # Render the image onto the layer
            self.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
            self.image.release()
            self.image = self.layers.texture  # Get the texture of the layer

    def draw(self, target):
        self.blurstate.set_uniform()#sets the blur radius
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)  # Shader render

    def release_texture(self):  # Called when .kill() and when emptying the group
        self.image.release()
        if self.layers:  # Release layer if it exists
            self.layers.release()

class BG_Fade(BG_Block):
    def __init__(self, pos, game_objects, img, parallax, positions):
        super().__init__(pos, game_objects, img, parallax)
        self.shader_state = states_shader.Idle(self)
        self.make_hitbox(positions, pos)
        self.interacted = False
        self.sounds = read_files.load_sounds_list('audio/SFX/bg_fade/')

    def make_hitbox(self, positions, offset_position):#the rect is the whole screen, need to make it correctly cover the surface part, some how
        x, y = [],[]
        for pos in positions:
            x.append(pos[0]+offset_position[0])
            y.append(pos[1]+offset_position[1])
        width = max(x) - min(x)
        height = max(y) - min(y)
        self.hitbox = [min(x),min(y),width,height]

    def update(self):
        self.shader_state.update()

    def draw(self, target):#called before draw in group
        self.shader_state.draw()
        super().draw(target)

    def player_collision(self,player):
        if self.interacted: return
        self.game_objects.sound.play_sfx(self.sounds[0])
        self.shader_state.handle_input('alpha')
        self.interacted = True

class Conversation_bubbles(Staticentity):
    def __init__(self, pos, game_objects, text, lifetime = 200, size = (32,32)):
        super().__init__(pos, game_objects)
        self.render_text(text)

        self.lifetime = lifetime
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        Conversation_bubbles.layer = game_objects.game.display.make_layer(size)
        Conversation_bubbles.bg = game_objects.font.fill_text_bg(size, 'text_bubble')

    def release_texture(self):
        pass

    def update(self):
        self.time += self.game_objects.game.dt * 0.1
        self.update_vel()
        self.update_pos()
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:
            self.kill()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*self.game_objects.game.dt,self.true_pos[1] + self.velocity[1]*self.game_objects.game.dt]
        self.rect.topleft = self.true_pos

    def update_vel(self):
        self.velocity[1] = 0.25*math.sin(self.time)

    def render_text(self, text):
        texture = self.game_objects.font.render(text = text)
        self.game_objects.game.display.render(self.bg, self.layer)#shader render
        self.game_objects.game.display.render(texture, self.layer, position = [10, self.rect[3]])#shader render
        self.image = self.layer.texture
        texture.release()

#shaders -> should this be here or in enteties_parallx?
class Portal(Staticentity):#portal to make a small spirit world with challenge rooms
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.bg_distort_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#bg
        self.bg_grey_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#entetirs

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0
        self.radius = 0
        self.thickness = 0

        self.state = kwarg.get('state', None)

        game_objects.interactables.add(Place_holder_interacatble(self, game_objects))#add a dummy interactable to the group, since portal cannot be in inetracatles
        game_objects.render_state.handle_input('portal', portal = self)

    def release_texture(self):
        self.game_objects.render_state.handle_input('idle')#go back to normal rendering
        self.empty_layer.release()
        self.noise_layer.release()
        self.screen_copy.release()
        self.bg_grey_layer.release()
        self.bg_distort_layer.release()

    def interact(self):#when player press T at place holder interactavle
        self.currentstate.handle_input('grow')

    def update(self):
        self.currentstate.update()#handles the radius and thickness of portal
        self.time += self.game_objects.game.dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort']['shine'] = False
        self.game_objects.shaders['distort']['TIME'] = self.time
        self.game_objects.shaders['distort']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['distort']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort']['center'] = [self.rect.center[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.center[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['distort']['radius'] = self.radius
        self.game_objects.shaders['distort']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.shaders['distort']['shine'] = True
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.empty_layer, shader = self.game_objects.shaders['distort'])#make them grey
        self.game_objects.game.display.render(self.empty_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['bloom'])

class Lighitning(Staticentity):#a shader to make lighning barrier
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos, game_objects)
        self.parallax = parallax

        self.image = game_objects.game.display.make_layer(size).texture
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self):
        self.time += self.game_objects.game.dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['lightning']['TIME'] = self.time
        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['lightning'])

    def player_collision(self):#player collision
        self.game_objects.player.take_dmg(1)
        self.game_objects.player.currentstate.handle_input('interrupt')#interupts dash
        pm_one = sign(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
        self.game_objects.player.knock_back([pm_one,0])

    def player_noncollision(self):
        pass

class Bubble_gate(Staticentity):#a shader to make bubble barrier
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.image = self.game_objects.game.display.make_layer(size).texture#TODO
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.time = 0

    def player_noncollision(self):
        pass

    def player_collision(self):
        self.game_objects.player.velocity[0] += (self.game_objects.player.hitbox.centerx - self.hitbox.centerx)*0.02

    def update(self):
        self.time += self.game_objects.game.dt*0.01

    def draw(self, target):
        self.game_objects.shaders['bubbles']['TIME'] = self.time
        pos =  (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.game_objects.shaders['bubbles'])#int seem nicer than round

    def release_texture(self):#called when .kill() and empty group
        self.image.release()

class Beam(Staticentity):
    def __init__(self, pos, game_objects, paralax, size):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size).texture
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self):
        self.time += self.game_objects.game.dt * 0.1

    def draw(self, target):
        self.game_objects.shaders['beam']['TIME'] = self.time
        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['beam'])#shader render

class Sky(Staticentity):
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos,game_objects)
        self.parallax = parallax

        self.empty = game_objects.game.display.make_layer(size)
        self.empty2 = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        self.size = size
        self.time = 0

    def release_texture(self):
        self.empty.release()
        self.empty2.release()
        self.noise_layer.release()

    def update(self):
        self.time += self.game_objects.game.dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] =self.time*0.1
        self.game_objects.shaders['noise_perlin']['scroll'] =[0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [10,10]#"standard"
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['cloud']['TIME'] = self.time
        self.game_objects.shaders['cloud']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['cloud']['scroll'] = [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]

        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = blit_pos,shader = self.game_objects.shaders['cloud'])

class Waterfall(Staticentity):
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos,game_objects)
        self.parallax = parallax

        self.size = size
        self.empty = game_objects.game.display.make_layer(size)
        self.screen_copy = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        self.time = 5#offset the time

    def release_texture(self):
        self.empty.release()
        self.noise_layer.release()
        self.screen_copy.release()

    def update(self):
        self.time += self.game_objects.game.dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.001
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [70,20]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.screen_copy)#make a copy of the screen

        #water
        self.game_objects.shaders['waterfall']['refraction_map'] = self.noise_layer.texture
        self.game_objects.shaders['waterfall']['water_mask'] = self.noise_layer.texture
        self.game_objects.shaders['waterfall']['SCREEN_TEXTURE'] = self.screen_copy.texture#for some reason, the water fall there, making it flicker. offsetting the cutout part, the flickering appears when the waterfall enetrs
        self.game_objects.shaders['waterfall']['TIME'] = self.time

        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['waterfall']['section'] = [blit_pos[0],blit_pos[1],self.size[0],self.size[1]]
        self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['waterfall'])

class Reflection(Staticentity):#water
    def __init__(self, pos, game_objects, parallax, size, dir, texture_parallax = 1, speed = 0, offset = 10):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.offset = offset
        self.squeeze = 1#the water flickers if it is not 1
        self.reflect_rect = pygame.Rect(self.rect.left, self.rect.top, size[0], size[1]/self.squeeze)

        self.empty = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.water_noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        #self.game_objects.shaders['water']['u_resolution'] = game_objects.game.window_size
        self.texture_parallax = texture_parallax#0 means no parallax on the texture

        self.time = 0
        self.water_speed = speed
        self.blur_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.colour = (0.39, 0.78, 1, 1)

    def release_texture(self):#called when .kill() and empty group
        self.empty.release()
        self.noise_layer.release()
        self.water_noise_layer.release()
        self.blur_layer.release()

    def update(self):
        self.time += self.game_objects.game.dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [10,10]#"standard"
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['noise_perlin']['scale'] = [10,80]# make it elongated along x, and short along y
        self.game_objects.game.display.render(self.empty.texture, self.water_noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #water
        self.game_objects.shaders['water_perspective']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['water_perspective']['noise_texture2'] = self.water_noise_layer.texture
        self.game_objects.shaders['water_perspective']['TIME'] = self.time
        self.game_objects.shaders['water_perspective']['SCREEN_TEXTURE'] = self.game_objects.game.screen.texture#stuff to reflect
        self.game_objects.shaders['water_perspective']['water_speed'] = self.water_speed
        self.game_objects.shaders['water_perspective']['water_albedo'] = self.colour
        self.game_objects.shaders['water_perspective']['texture_parallax'] =self.texture_parallax

        self.reflect_rect.bottomleft = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], -self.offset + self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]# the part to cut
        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['water_perspective']['section'] = [self.reflect_rect[0],self.reflect_rect[1],self.reflect_rect[2],self.reflect_rect[3]]

        #final rendering -> tmporary fix TODO
        if self.parallax[0] == 1:#don't blur if there is no parallax
            self.game_objects.game.display.render(self.noise_layer.texture, self.game_objects.game.screen, position = blit_pos, section = self.reflect_rect, scale = [1, self.squeeze], shader = self.game_objects.shaders['water_perspective'])
        else:
            self.game_objects.shaders['blur']['blurRadius'] = 1/self.parallax[0]#set the blur redius
            self.game_objects.game.display.render(self.noise_layer.texture, self.blur_layer, shader = self.game_objects.shaders['water_perspective'])
            self.game_objects.game.display.render(self.blur_layer.texture, self.game_objects.game.screen, position = blit_pos, section = self.reflect_rect, scale = [1, self.squeeze], shader = self.game_objects.shaders['blur'])

class God_rays(Staticentity):
    def __init__(self, pos, game_objects, parallax, size, **properties):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.image = game_objects.game.display.make_layer(size).texture
        self.shader = game_objects.shaders['rays']
        self.shader['resolution'] = self.game_objects.game.window_size
        self.time = 0
        self.colour = properties.get('colour',(1.0, 0.9, 0.65, 0.6))#colour
        self.angle = properties.get('angle',-0.2)#radians
        self.position = properties.get('position',(0,0))#in pixels
        self.falloff = properties.get('falloff',(0,0.3))#between 0 and 1

    def release_texture(self):
        self.image.release()

    def update(self):
        self.time += self.game_objects.game.dt * 0.1

    def draw(self, target):
        self.shader['angle'] = self.angle
        self.shader['position'] = self.position
        self.shader['falloff'] = self.falloff
        self.shader['time'] = self.time
        self.shader['size'] = self.image.size
        self.shader['color'] = self.colour

        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = pos, shader = self.shader)#shader render

class TwoD_liquid(Staticentity):
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.empty = game_objects.game.display.make_layer(size)
        self.screen_copy = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.hitbox = pygame.Rect(pos, size)#for player collision
        self.interacted = False#for player collision

        self.time = 0
        self.size = size

        self.shader = game_objects.shaders['twoD_liquid']
        self.shader['u_resolution'] = self.game_objects.game.window_size
        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            if not properties.get('vertical', False):
                self.hole = Hole(pos, game_objects, size)#for poison
                self.currentstate = states_twoD_liquid.Poison(self, **properties)
            else:#vertical scroller -> golden fields
                self.currentstate = states_twoD_liquid.Poison_vertical(self, **properties)
        else:
            self.currentstate = states_twoD_liquid.Water(self, **properties)

    def release_texture(self):
        self.empty.release()
        self.screen_copy.release()
        self.noise_layer.release()

    def update(self):
        self.time += self.game_objects.game.dt
        self.currentstate.update()

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [10,10]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.screen_copy)#make a copy of the screen
        #water
        self.game_objects.shaders['twoD_liquid']['refraction_map'] = self.noise_layer.texture
        self.game_objects.shaders['twoD_liquid']['SCREEN_TEXTURE'] = self.screen_copy.texture#for some reason, the water fall there, making it flicker. offsetting the cutout part, the flickering appears when the waterfall enetrs
        self.game_objects.shaders['twoD_liquid']['TIME'] = self.time * 0.01

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.shaders['twoD_liquid']['section'] = [pos[0], pos[1], self.size[0], self.size[1]]

        self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = pos, shader = self.shader)#shader render

    def player_collision(self, player):#player collision
        if self.interacted: return
        player.friction = [player.friction[0] * 2, player.friction[1] * 2]
        vel_scale = player.velocity[1] / C.max_vel[1]
        self.splash(player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [7 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        player.timer_jobs['wet'].deactivate()#stop dropping if inside the water again
        self.interacted = True
        self.currentstate.player_collision(player)

    def player_noncollision(self):
        if not self.interacted: return
        self.game_objects.player.friction = C.friction_player.copy()
        self.game_objects.player.timer_jobs['wet'].activate(self.currentstate.liquid_tint)#water when player leaves
        vel_scale = abs(self.game_objects.player.velocity[1] / C.max_vel[1])
        self.splash(self.game_objects.player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [10 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        self.interacted = False
        self.currentstate.player_noncollision()

    def splash(self,  pos, number_particles=20, **kwarg):#called from states, upoin collusions
        for i in range(0, number_particles):
            obj1 = particles.Circle(pos, self.game_objects, **kwarg)
            self.game_objects.cosmetics.add(obj1)

class Up_stream(Staticentity):
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.hitbox = pygame.Rect(pos, size)
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self):
        self.time += self.game_objects.game.dt

    def draw(self, target):
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['up_stream'])#shader render

    def player_collision(self, player):#player collision
        player.velocity[1] -= self.game_objects.game.dt*0.5

    def player_noncollision(self):
        pass

class Smoke(Staticentity):
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.hitbox = pygame.Rect(pos, size)
        self.time = 0
        self.size = size

        self.colour = properties.get('colour', (1,1,1,1))
        self.spawn_rate = int(properties.get('spawn_rate', 10))
        self.radius = properties.get('radius', 0.03)
        self.speed = properties.get('speed', 0.2)
        self.horizontalSpread = properties.get('horizontalSpread', 0.5)
        self.lifetime = properties.get('lifetime', 2)
        self.spawn_position = properties.get('spawn_position', (0.5, 0.0))

    def release_texture(self):
        self.image.release()

    def update(self):
        self.time += self.game_objects.game.dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['smoke']['noiseTexture'] = self.noise_layer.texture
        self.game_objects.shaders['smoke']['time'] = self.time*0.01
        self.game_objects.shaders['smoke']['textureSize'] = self.size

        self.game_objects.shaders['smoke']['baseParticleColor'] = self.colour
        self.game_objects.shaders['smoke']['spawnRate'] = self.spawn_rate
        self.game_objects.shaders['smoke']['baseParticleRadius'] = self.radius
        self.game_objects.shaders['smoke']['baseParticleSpeed'] = self.speed
        self.game_objects.shaders['smoke']['horizontalSpread'] = self.horizontalSpread
        self.game_objects.shaders['smoke']['particleLifetime'] = self.lifetime
        self.game_objects.shaders['smoke']['spawnPosition'] = self.spawn_position

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['smoke'])#shader render

#normal animation
class Animatedentity(Staticentity):#animated stuff, i.e. cosmetics
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):#called from aniumation when the animation is finished
        self.currentstate.increase_phase()

    def release_texture(self):#called when .kill() and empty group
        for state in self.sprites.keys():
            for frame in range(0,len(self.sprites[state])):
                self.sprites[state][frame].release()

class BG_Animated(Animatedentity):
    def __init__(self, game_objects, pos, sprite_folder_path, parallax = (1,1)):
        super().__init__(pos,game_objects)
        self.sprites = {'idle': read_files.load_sprites_list(sprite_folder_path, game_objects)}
        self.image = self.sprites['idle'][0]
        self.parallax = parallax

    def update(self):
        self.animation.update()

    def reset_timer(self):#animation need it
        pass

class Platform_entity(Animatedentity):#Things to collide with platforms
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = {'ramp': True, 'one_way':True}#a flag for entities to go through ramps from side or top
        self.velocity = [0,0]
        self.running_particles = Dust_running_particles#default particles while runing

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    def update_rect_y(self):
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos[1] = self.rect.top

    def update_rect_x(self):
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos[0] = self.rect.left

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.true_pos = list(self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    def update_true_pos_x(self):#called from Engine.platform collision. The velocity to true pos need to be set in collision if group distance should work proerly for enemies (so that the velocity is not applied when removing the sprite from gorup)
        self.true_pos[0] += self.slow_motion*self.game_objects.game.dt*self.velocity[0]
        self.rect.left = int(self.true_pos[0])#should be int
        self.update_hitbox()

    def update_true_pos_y(self):#called from Engine.platform collision
        self.true_pos[1] += self.slow_motion*self.game_objects.game.dt*self.velocity[1]
        self.rect.top = int(self.true_pos[1])#should be int
        self.update_hitbox()

    #ramp collisions
    def ramp_top_collision(self, position):#called from collusion in clollision_ramp
        self.hitbox.top = position
        self.collision_types['top'] = True
        self.velocity[1] = 2#need to have a value to avoid "dragin in air" while running
        self.velocity[0] = 0#need to have a value to avoid "dragin in air" while running

    def ramp_down_collision(self, position):#called from collusion in clollision_ramp
        self.hitbox.bottom = position
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')
        self.velocity[1] = C.max_vel[1] + 10#make aila sticj to ground to avoid falling animation: The extra gravity on ramp

    #pltform collisions.
    def right_collision(self, block):
        self.hitbox.right = block.hitbox.left
        self.collision_types['right'] = True
        self.currentstate.handle_input('Wall')

    def left_collision(self, block):
        self.hitbox.left = block.hitbox.right
        self.collision_types['left'] = True
        self.currentstate.handle_input('Wall')

    def down_collision(self, block):
        self.hitbox.bottom = block.hitbox.top
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = 0

    def limit_y(self):#limits the velocity on ground, onewayup. But not on ramps: it makes a smooth drop
        self.velocity[1] = 1.2/self.game_objects.game.dt

class Character(Platform_entity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()

        self.timers = []#a list where timers are append whe applicable, e.g. jump, invincibility etc.
        self.shader_state = states_shader.Idle(self)

    def update(self):
        self.update_timers()
        self.update_vel()#need to be after update_timers since jump will add velocity in update_timers
        self.currentstate.update()#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update()#need to be after currentstate since animation will animate the current state
        self.shader_state.update()

    def update_vel(self):
        self.velocity[1] += self.slow_motion*self.game_objects.game.dt*(self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1],self.max_vel[1]/self.game_objects.game.dt)#set a y max speed#
        self.velocity[0] += self.slow_motion*self.game_objects.game.dt*(self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def take_dmg(self,dmg):
        if self.invincibile: return
        self.health -= dmg

        if self.health > 0:#check if dead¨
            self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period (minimum time needed to that the swrod doesn't hit every frame)
            self.shader_state.handle_input('Hurt')#turn white
            self.AI.handle_input('Hurt')
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            #self.game_objects.game.state_stack[-1].handle_input('dmg', duration = 15, amplitude = 10)#makes the game freez for few frames
            self.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
        else:#if dead
            self.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
            #self.game_objects.game.state_stack[-1].handle_input('dmg', duration = 15, amplitude = 30)#makes the game freez for few frames
            self.aggro = False
            self.invincibile = True
            self.AI.deactivate()
            self.currentstate.enter_state('Death')#overrite any state and go to deat

    def knock_back(self, dir):
        self.velocity[0] = dir[0] * 30 * (1 - abs(dir[1]))
        self.velocity[1] = -dir[1] * 10

    def hurt_particles(self, type='Circle', number_particles=20, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, type)(self.hitbox.center, self.game_objects, **kwarg)
            self.game_objects.cosmetics.add(obj1)

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def draw(self, target):
        self.shader_state.draw()#for entetirs to turn white
        super().draw(target)

class Player(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/aila/')
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/aila/texture/', game_objects)
        self.normal_maps = read_files.load_sprites_dict('Sprites/enteties/aila/normal/', game_objects)
        self.image = self.sprites['idle_main'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes

        self.max_health = 100
        self.max_spirit = 4
        self.health = 100
        self.spirit = 2

        self.projectiles = game_objects.fprojectiles
        self.sword = Aila_sword(self)
        self.abilities = Player_abilities(self)#spirit (thunder,migawari etc) and movement /dash, double jump and wall glide)

        self.states = {'Idle':True,'Walk':True,'Run':True,'Pray':True,'Stand_up':True,
                     'Jump':True,'Fall':True,'Death':True,
                     'Invisible':True,'Hurt':True,'Spawn':True,'Plant_bone':True,
                     'Sword_run1':True,'Sword_run2':True,'Sword_stand1':True,'Sword_stand2':True,
                     'Air_sword2':True,'Air_sword1':True,'Sword_up':True,'Sword_down':True,
                     'Dash_attack':True,'Ground_dash':True,'Air_dash':False,'Wall_glide':False,'Double_jump':False,
                     'Thunder':True,'Shield':True,'Migawari':True,'Slow_motion':True,
                     'Bow':True,'Counter':True, 'Sword_fall':True,
                     'Sword_jump1':True, 'Sword_jump2':True, 'Dash_jump':True}
        self.currentstate = states_player.Idle_main(self)
        self.death_state = states_death.Idle(self)#this one can call "normal die" or specifal death (for example cultist encounter)

        self.spawn_point = {'map': 'light_forest_1', 'point': '1', 'safe_spawn' : [0,0]}#can append bone
        self.inventory = {'Amber_Droplet':403,'Bone':2,'Soul_essence':10,'Tungsten':10}#the keys need to have the same name as their respective classes
        self.omamoris = Omamoris(self)#
        self.flags = {'ground': True, 'sword_swinging': False}# a flag to check if on graon (used for jumpåing), #a flag to make sure you can only swing sword when this is False

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_player),'jump_buffer':Jump_buffer_timer(self,C.jump_buffer_timer_player),
                        'sword':Sword_timer(self, C.sword_time_player),'shroomjump':Shroomjump_timer(self,C.shroomjump_timer_player),'ground':Cayote_timer(self,C.cayote_timer_player),
                        'air':Air_timer(self,C.air_timer),'wall':Wall_timer(self,C.wall_timer),'wall_2':Wall_timer_2(self,C.wall_timer_2),
                        'wet':Wet_timer(self, 60), 'dash_buffer':Dash_buffer_timer(self, C.jump_buffer_timer_player),}#these timers are activated when promt and a job is appeneded to self.timer.
        self.reset_movement()
        self.tjasolmais_embrace = None

    def update_hitbox(self):
        super().update_hitbox()
        self.sword.update_hitbox()

    def ramp_down_collision(self, position):#when colliding with platform beneth
        super().ramp_down_collision(position)
        self.flags['ground'] = True#used for jumping
        self.friction = C.friction_player.copy()

    def down_collision(self, block):#when colliding with platform beneth
        super().down_collision(block)
        self.flags['ground'] = True#used for jumping
        self.friction = C.friction_player.copy()

    def take_dmg(self, dmg = 1, duration = 20):
        if self.tjasolmais_embrace: self.tjasolmais_embrace.take_dmg(dmg)
        if self.invincibile: return
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
        self.health -= dmg*self.dmg_scale#a omamori can set the dmg_scale to 0.5
        self.game_objects.UI['gameplay'].remove_hearts(dmg*self.dmg_scale)#update UI

        if self.health > 0:#check if dead¨
            self.shader_state.handle_input('Hurt')#turn white
            self.shader_state.handle_input('Invincibile')#blink a bit
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state or interupt attacks?
            self.hurt_particles(lifetime = 40, vel = {'linear':[4,7]}, colour=[0,0,0,255], scale=3, number_particles=60)
            self.game_objects.cosmetics.add(Slash(self.hitbox.center,self.game_objects))#make a slash animation
            new_game_state = states.Pause_gameplay(self.game_objects.game, duration = duration, amplitude = 10)#pause the game for a while with an optional shake
            new_game_state.enter_state()
            self.game_objects.shader_render.append_shader('chromatic_aberration', duration = 20)
        else:#if health < 0
            self.die()
        return True#return truw to show that damage was taken

    def die(self):#also called from vertical acid
        self.death_state.die()#depending on gameplay state, different death stuff should happen
        self.animation.update()#make sure you get the new animation
        self.game_objects.cosmetics.add(Blood(self.hitbox.center, self.game_objects, dir = self.dir))

        new_game_state = states.Slow_gameplay(self.game_objects.game, duration = 100, rate = 0.4)#pause the game for a while with an optional shake
        new_game_state.enter_state()

        new_game_state = states.Pause_gameplay(self.game_objects.game, duration = 50)#pause the game for a while with an optional shake
        new_game_state.enter_state()

    def heal(self, health = 1):
        self.health += health
        self.game_objects.UI['gameplay'].update_hearts()#update UI

    def consume_spirit(self, spirit = 1):
        self.spirit -= spirit
        self.game_objects.UI['gameplay'].remove_spirits(spirit)#update UI

    def add_spirit(self, spirit = 1):
        self.spirit += spirit
        self.game_objects.UI['gameplay'].update_spirits()#update UI

    def dead(self):#called when death animation is finished
        self.game_objects.world_state.update_statistcis('death')#count the number of times aila has died
        new_game_state = states.Death(self.game_objects.game)
        new_game_state.enter_state()

    def reset_movement(self):#called when loading new map or entering conversations
        self.acceleration =  [0, C.acceleration[1]]
        self.friction = C.friction_player.copy()

    def update(self):
        super().update()
        self.omamoris.update()

    def draw(self, target):#called in group
        self.shader_state.draw()
        pos = (round(self.true_pos[0]-self.game_objects.camera_manager.camera.true_scroll[0]),round(self.true_pos[1]-self.game_objects.camera_manager.camera.true_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, flip = bool(max(self.dir[0],0)), shader = self.shader)#shader render

        #normal map draw
        self.game_objects.shaders['normal_map']['direction'] = -self.dir[0]# the normal map shader can invert the normal map depending on direction
        self.game_objects.game.display.render(self.normal_maps[self.state][self.animation.image_frame], self.game_objects.lights.normal_map, position = pos, flip = bool(max(self.dir[0],0)), shader = self.game_objects.shaders['normal_map'])#should be rendered on the same position, image_state and frame as the texture

class Maderakkas_reflection_entity(Character):#player double ganger
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = Maderakkas_reflection_entity.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1]-5,16,16)#add a smalll ofset in y to avoid collision
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes
        self.invincibile = False
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_player)}#these timers are activated when promt and a job is appeneded to self.timer.
        self.health = kwarg.get('health', 1)
        self.lifetime = kwarg.get('lifetime', 1000)

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destroy()

    def take_dmg(self,dmg):
        if self.invincibile: return
        self.health -= dmg

        if self.health > 0:#check if dead¨
            self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
            #self.shader_state.handle_input('Hurt')#turn white
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
        else:#if dead
            self.invincible = True
            self.currentstate.enter_state('Death')#overrite any state and go to deat
            if self.game_objects.player.abilities.spirit_abilities['Migawari'].level == 3:
                self.game_objects.player.heal(1)

    def destroy(self):
        if self.lifetime < 0:
            self.currentstate.handle_input('Death')

    def release_texture(self):
        pass

    def pool(game_objects):
        Maderakkas_reflection_entity.sprites = read_files.load_sprites_dict('Sprites/attack/migawari/', game_objects)

class Enemy(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause
        self.description = 'enemy'##used in journal
        self.original_pos = pos

        self.currentstate = states_enemy.Idle(self)
        self.AI = AI_enemy.AI(self)

        self.inventory = {'Amber_Droplet':random.randint(0,10),'Bone':1,'Heal_item':1}#thigs to drop wgen killed
        self.spirit = 10
        self.health = 3

        self.aggro = True#colliding with player
        self.dmg = 1#projectile damage

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

        self.attack_distance = [0,0]#at which distance to the player to attack
        self.aggro_distance = [100,50]#at which distance to the player when you should be aggro. Negative value make it no going aggro

    def update(self):
        super().update()
        self.AI.update()#tell what the entity should do
        self.group_distance()

    def player_collision(self, player):#when player collides with enemy
        if not self.aggro: return
        if player.invincibile: return
        player.take_dmg(1)
        pm_one = sign(player.hitbox.center[0]-self.hitbox.center[0])
        player.knock_back([pm_one,0])

    def dead(self):#called when death animation is finished
        self.loots()
        self.game_objects.world_state.update_kill_statistics(type(self).__name__.lower())
        self.kill()

    def loots(self):#called when dead
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop,self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key] = 0

    def countered(self):#purple infifite stone
        self.velocity[0] = -30*self.dir[0]
        self.currentstate = states_enemy.Stun(self,duration=30)#should it overwrite?

    def health_bar(self):#called from omamori Boss_HP
        pass

    def chase(self, position = [0,0]):#called from AI: when chaising
        self.velocity[0] += self.dir[0]*0.6

    def patrol(self, position = [0,0]):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3

class Flying_enemy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8,C.friction[0]*0.8]

        self.max_vel = [C.max_vel[0],C.max_vel[0]]
        self.dir[1] = 1
        self.AI = AI_enemy_flying.Patrol(self)
        self.currentstate = states_enemy_flying.Idle(self)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def knock_back(self,dir):
        amp = [30,30]
        self.velocity[0] = dir[0]*amp[0]
        self.velocity[1] = -dir[1]*amp[1]

    def chase(self, target_distance):#called from AI: when chaising
        self.velocity[0] += (target_distance[0])*0.002 + self.dir[0]*0.1
        self.velocity[1] += (target_distance[1])*0.002 + sign(target_distance[1])*0.1

    def patrol(self, position):#called from AI: when patroling
        self.velocity[0] += 0.001*(position[0]-self.rect.centerx)
        self.velocity[1] += 0.001*(position[1]-self.rect.centery)

    def walk(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.3)
        self.velocity[1] += amp*math.sin(5*time)# - self.entity.dir[1]*0.1

    def update_rect_y(self):
        self.rect.center = self.hitbox.center
        self.true_pos[1] = self.rect.top

    def update_rect_x(self):
        self.rect.center = self.hitbox.center
        self.true_pos[0] = self.rect.left

    def killed(self):#called when death animation starts playing
        pass

    def limit_y(self):
        pass

class Flower_butterfly(Flying_enemy):#peaceful ones
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/flower_butterfly/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 1
        self.aggro_distance = [0,0]
        self.game_objects.lights.add_light(self, colour = [77/255,168/255,177/255,200/255], interact = False)
        self.aggro = False

    def update(self):
        super().update()
        obj1 = particles.Floaty_particles(self.rect.center, self.game_objects, distance = 0, vel = {'linear':[0.1,-1]}, dir = 'isotropic')
        self.game_objects.cosmetics2.add(obj1)

class Mygga(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 30
        self.aggro_distance = [130, 80]
        self.AI = AI_mygga.Patrol(self)
        self.accel = [0.013, 0.008]
        self.accel_chase = [0.026, 0.009]
        self.deaccel_knock = 0.84
        self.max_chase_vel = 1.8
        self.max_patrol_vel = 1.2
        self.friction = [0.009,0.009]

    def knock_back(self,dir):
        self.AI.enter_AI('Knock_back')
        amp = 19
        if dir[1] != 0:
            self.velocity[1] = -dir[1] * amp
        else:
            self.velocity[0] = dir[0] * amp

    def player_collision(self, player):#when player collides with enemy
        super().player_collision(player)
        self.velocity = [0, 0]
        self.AI.enter_AI('Wait', time = 30, next_AI = 'Chase')

    def patrol(self, position):#called from AI: when patroling
        self.velocity[0] += sign(position[0] - self.rect.centerx) * self.accel[0]
        self.velocity[1] += sign(position[1] - self.rect.centery) * self.accel[1]
        self.velocity[0] = min(self.max_chase_vel, self.velocity[0])
        self.velocity[1] = min(self.max_chase_vel, self.velocity[1])

    def chase(self, target_distance):#called from AI: when chaising
        self.velocity[0] += sign(target_distance[0]) * self.accel_chase[0]
        self.velocity[1] += sign(target_distance[1]) * self.accel_chase[1]
        for i in range(2):
            if abs(self.velocity[i]) > self.max_chase_vel:
                self.velocity[i] = sign(self.velocity[i]) *  self.max_chase_vel

    def chase_knock_back(self, target_distance):#called from AI: when chaising
        self.velocity[0] *= self.deaccel_knock#sign(target_distance[0])
        self.velocity[1] *= self.deaccel_knock#sign(target_distance[1])

    def walk(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.008)
        self.velocity[1] += amp*math.sin(2.2*time)# - self.entity.dir[1]*0.1

class Mygga_torpedo(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga_torpedo/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 30
        self.AI = AI_mygga.Patrol(self)

        self.aggro_distance = [180,130]
        self.attack_distance = [150,100]

        self.accel = [0.013, 0.008]
        self.accel_chase = [0.026, 0.009]
        self.deaccel_knock = 0.88
        self.max_chase_vel = 1.8
        self.max_patrol_vel = 1.2
        self.friction = [0.009,0.009]

    def knock_back(self,dir):
        self.AI.enter_AI('Knock_back')
        amp = [16,16]
        self.velocity[0] = dir[0]*amp[0]
        self.velocity[1] = -dir[1]*amp[1]

    def player_collision(self, player):#when player collides with enemy
        super().player_collision(player)
        self.velocity = [0, 0]
        self.AI.enter_AI('Wait', time = 30, next_AI = 'Chase')

    def patrol(self, position):#called from AI: when patroling
        self.velocity[0] += sign(position[0] - self.rect.centerx) * self.accel[0]
        self.velocity[1] += sign(position[1] - self.rect.centery) * self.accel[1]
        self.velocity[0] = min(self.max_chase_vel, self.velocity[0])
        self.velocity[1] = min(self.max_chase_vel, self.velocity[1])

    def chase(self, target_distance):#called from AI: when chaising
        self.velocity[0] += sign(target_distance[0]) * self.accel_chase[0]
        self.velocity[1] += sign(target_distance[1]) * self.accel_chase[1]
        for i in range(2):
            if abs(self.velocity[i]) > self.max_chase_vel:
                self.velocity[i] = sign(self.velocity[i]) *  self.max_chase_vel

    def chase_knock_back(self, target_distance):#called from AI: when chaising
        self.velocity[0] *= self.deaccel_knock#sign(target_distance[0])
        self.velocity[1] *= self.deaccel_knock#sign(target_distance[1])

    def walk(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.008)
        self.velocity[1] += amp*math.sin(2.2*time)# - self.entity.dir[1]*0.1

class Mygga_suicide(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga_torpedo/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 1
        self.AI = AI_mygga.Patrol(self)

        self.aggro_distance = [180,130]
        self.attack_distance = self.aggro_distance.copy()

    def chase(self, position = [0,0]):#called from AI: when chaising
        pass

    def patrol(self, position = [0,0]):#called from AI: when patroling
        pass

    def player_collision(self, player):#when player collides with enemy
        self.suicide()

    def killed(self):#called when death animation starts playing
        self.suicide()

    def suicide(self):#called from states
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration

    #pltform collisions.
    def right_collision(self, block):
        super().right_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def left_collision(self, block):
        super().left_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def down_collision(self, block):
        super().down_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def top_collision(self, block):
        super().top_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def ramp_down_collision(self, position):#called from collusion in clollision_ramp
        super().ramp_down_collision(position)
        self.currentstate.handle_input('collision')#for suicide

    def ramp_top_collision(self, position):#called from collusion in clollision_ramp
        super().ramp_top_collision(position)
        self.currentstate.handle_input('collision')#for suicide

class Mygga_roaming(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.velocity = [random.randint(-3,3),random.randint(-3,3)]
        self.dir[0] = sign(self.velocity[0])
        self.AI.enter_AI('roaming_attack', frequency = 150)

    def attack(self):#called from roaming AI
        dirs = [[1,1],[-1,1],[1,-1],[-1,-1]]
        for direction in dirs:
            obj = Projectile_1(self.hitbox.center, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)

    def walk(self, time):#called from walk state
        pass

    def update_vel(self):
        pass

    #ramp collisions
    def ramp_top_collision(self, position):#called from collusion in clollision_ramp
        self.hitbox.top = position
        self.collision_types['top'] = True
        self.velocity[1] *= -1

    def ramp_down_collision(self, position):#called from collusion in clollision_ramp
        self.hitbox.bottom = position
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1

    #platform collision
    def right_collision(self, block):
        super().right_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = -1

    def left_collision(self, block):
        super().left_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = 1

    def down_collision(self, block):
        super().down_collision(block)
        self.velocity[1] *= -1

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] *= -1

class Exploding_mygga(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/exploding_mygga/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 4
        self.attack_distance = [20,20]
        self.aggro_distance = [150,100]
        self.currentstate = states_exploding_mygga.Idle(self)

    def killed(self):
        self.projectiles.add(Hurt_box(self, size = [64,64], lifetime = 30))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration

class Froggy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/froggy/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health = 1
        self.aggro = 0
        self.attack_distance = [150,50]

        self.currentstate = states_froggy.Idle(self)
        self.shader_state = states_shader.Idle(self)
        self.AI = AI_froggy.AI(self)
        self.inventory = {'Amber_Droplet':random.randint(5,15)}#thigs to drop wgen killed

    def knock_back(self,dir):
        pass

class Packun(Enemy):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/packun/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health = 3
        self.dmg = 1
        self.attack_distance = [250,50]

    def attack(self):#called from states, attack main
        attack = Projectile_1(self.rect.topleft, self.game_objects)#make the object
        self.projectiles.add(attack)#add to group but in main phase

    def chase(self, position):#called from AI
        pass

    def patrol(self,position):
        pass

class Sandrew(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/sandrew/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [200,25]
        self.aggro_distance = [250,25]#at which distance to the player when you should be aggro. Negative value make it no going aggro

class Slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Slime.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 16, 16)
        self.aggro_distance = [200,20]#at which distance to the player when you should be aggro -> negative means no
        self.health = 2

    def release_texture(self):
        pass

    def pool(game_objects):#spawned in mid game by sline giant
        Slime.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/slime/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')

class Slime_giant(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/slime_giant/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],48,48)
        self.number = random.randint(2, 6)#number of minions
        self.aggro_distance = [200,20]#at which distance to the player when you should be aggro -> negative means no

    def loots(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery-10]
        for i in range(0,self.number):
            obj = Slime(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Wall_slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/wall_slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()#pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate.enter_state('Walk')
        self.AI = AI_wall_slime.Peace(self)

    def knock_back(self,dir):
        pass

    def update_vel(self):
        self.velocity[1] = self.acceleration[1]-self.dir[1]
        self.velocity[0] = self.acceleration[0]+self.dir[0]

class Vatt(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/vatt/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)
        self.health = 3
        self.spirit = 3
        self.aggro = False
        self.currentstate = states_vatt.Idle(self)
        self.attack_distance = [60, 30]
        self.AI = AI_vatt.AI(self)

    def turn_clan(self):#this is acalled when tranformation is finished
        for enemy in self.game_objects.enemies.sprites():
            if type(enemy).__name__=='Vatt':
                enemy.aggro = True
                enemy.AI.handle_input('Hurt')

    def patrol(self, direction):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3 * direction[0]

class Maggot(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/maggot/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,30)
        self.currentstate = states_maggot.Fall_stand(self)
        self.AI = AI_maggot.Idle(self)
        self.health = 1
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period (minimum time needed to that the swrod doesn't hit every frame)
        self.friction[0] = C.friction[0]*2

class Larv_simple(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/larv_simple/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,30)
        self.attack_distance = [0,0]

class Larv_poison(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/larv/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.aggro_distance = [180,150]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack_distance = [200,180]

    def attack(self):#called from states, attack main
        attack = Poisonblobb(self.rect.topleft, self.game_objects, dir = self.dir)#make the object
        self.projectiles.add(attack)#add to group but in main phase

class Shroompoline(Enemy):#an enemy or interactable?
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=read_files.load_sprites_dict('Sprites/enteties/enemies/shroompolin/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box=pygame.Rect(pos[0],pos[1],32,10)
        self.aggro = False#player collision
        self.invincibile = True#taking dmg

    def player_collision(self,player):
        if self.game_objects.player.velocity[1]>0:#going down
            offset=self.game_objects.player.velocity[1]+1
            if self.game_objects.player.hitbox.bottom < self.jump_box.top+offset:
                self.currentstate.enter_state('Hurt')
                self.game_objects.player.currentstate.enter_state('Jump_stand_main')
                self.game_objects.player.velocity[1] = -10
                self.game_objects.player.timer_jobs['shroomjump'].activate()

    def update_hitbox(self):
        super().update_hitbox()
        self.jump_box.midtop = self.rect.midtop

    def chase(self):#called from AI: when chaising
        pass

    def patrol(self,position):#called from AI: when patroling
        pass

class Kusa(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.load_sprites_dict('Sprites/enteties/enemies/kusa/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = 30
        self.health = 1
        self.AI = AI_kusa.Peace(self)
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp=2,duration=30)#amplitude and duration

class Svampis(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=read_files.load_sprites_dict('Sprites/enteties/enemies/svampis/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = 30
        self.health = 1
        self.AI = AI_kusa.Peace(self)
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp=2,duration=30)#amplitude and duration

class Egg(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/enteties/enemies/egg/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.number = random.randint(1, 4)
        self.aggro_distance = -1 #if negative, it will not go into aggro

    def knock_back(self,dir):
        pass

    def death(self):
        self.spawn_minions()
        self.kill()

    def spawn_minions(self):
        pos = [self.hitbox.centerx,self.hitbox.centery-10]
        for i in range(0,self.number):
            obj = Slime(pos,self.game_objects)
            obj.velocity=[random.randint(-100, 100),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Cultist_rogue(Enemy):
    def __init__(self, pos, game_objects, gameplay_state = None):
        super().__init__(pos,game_objects)
        self.sprites=read_files.load_sprites_dict('Sprites/enteties/enemies/cultist_rogue/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 40, 40)
        self.health = 3
        self.attack_distance = [80,10]
        self.currentstate = states_rogue_cultist.Idle(self)
        self.gameplay_state = gameplay_state

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

    def dead(self):#called when death animation is finished
        super().dead()
        if self.gameplay_state: self.gameplay_state.incrase_kill()

class Cultist_warrior(Enemy):
    def __init__(self,pos,game_objects,gameplay_state=None):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/cultist_warrior/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 3
        self.attack_distance = [80,10]
        self.gameplay_state = gameplay_state

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

    def dead(self):#called when death animation is finished
        super().dead()
        if self.gameplay_state: self.gameplay_state.incrase_kill()

#animals
class Bird(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/enteties/animals/bluebird/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_bird.Idle(self)
        self.aggro = False
        self.health = 1
        self.AI = AI_bird.Idle(self)
        self.aggro_distance = [100,50]#at which distance is should fly away

    def knock_back(self,dir):
        pass

class NPC(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.group = game_objects.npcs
        self.pause_group = game_objects.entity_pause
        self.name = str(type(self).__name__)#the name of the class
        self.load_sprites()
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox

        self.currentstate = states_NPC.Idle(self)
        self.dialogue = dialogue.Dialogue(self)#handles dialoage and what to say
        self.define_conversations()

    def define_conversations(self):#should depend on NPC
        self.priority = ['reindeer','ape']#priority events to say
        self.event = ['aslat']#normal events to say
        self.quest = []

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict("Sprites/Enteties/NPC/" + self.name + "/animation/", self.game_objects)
        img = pygame.image.load('Sprites/enteties/NPC/' + self.name +'/potrait.png').convert_alpha()
        self.portrait = self.game_objects.game.display.surface_to_texture(img)#need to save in memoery

    def update(self):
        super().update()
        #self.group_distance()

    def render_potrait(self, terget):
        self.game_objects.game.display.render(self.portrait, terget, position = (50,100))#shader render

    def interact(self):#when plater press t
        new_state = states.Conversation(self.game_objects.game, self)
        new_state.enter_state()

    def random_conversation(self, text):#can say stuff through a text bubble
        random_conv = Conversation_bubbles(self.rect.topright,self.game_objects, text)
        self.game_objects.cosmetics.add(random_conv)

    def buisness(self):#enters after conversation
        pass

class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        if self.game_objects.world_state.state.get('reindeer', False):#if player has deafated the reindeer
            if not self.game_objects.player.states['Wall_glide']:#if player doesn't have wall yet (so it only enters once)
                new_game_state = states.Blit_image_text(self.game_objects.game,self.game.game_objects.player.sprites[Wall_glide][0].copy())
                new_game_state.enter_state()
                self.game_objects.player.states['Wall_glide'] = True

class Guide(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.shader_state = states_shader_guide.Idle(self)
        self.layer1 = self.game_objects.game.display.make_layer(self.image.size)#make a layer ("surface")TODO

    def update(self):
        super().update()
        self.shader_state.update()#goes between idle and teleport

    def buisness(self):#enters after conversation
        self.shader_state = states_shader_guide.Teleport(self)
        for i in range(0, 10):#should maybe be the number of abilites Aila can aquire?
            particle = getattr(particles, 'Circle')(self.hitbox.center,self.game_objects,distance=0,lifetime = -1,vel={'linear':[7,15]},dir='isotropic',scale=5,colour=[100,200,255,255],state = 'Circle_converge',gradient = 1)
            light = self.game_objects.lights.add_light(particle, colour = [100/255,200/255,255/255,255/255], radius = 20)
            particle.light = light#add light reference
            self.game_objects.cosmetics.add(particle)

    def give_light(self):#called when teleport shader is finished
        self.game_objects.lights.add_light(self.game_objects.player, colour = [200/255,200/255,200/255,200/255])
        self.game_objects.world_state.update_event('guide')

    def draw(self, target):#called in group
        self.shader_state.draw()
        pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, flip = bool(max(self.dir[0],0)), shader = self.shader)#shader render

class Sahkar(NPC):#deer handler
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Busty_baker(NPC):#bartender
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_Droplet':1}#itam+price
        text = self.dialogue.get_comment()
        self.random_conversation(text)

    def buisness(self):#enters after conversation
        new_state = states.Facilities(self.game_objects.game,'Vendor',self)
        new_state.enter_state()

class MrSmith(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        new_state = states.Facilities(self.game_objects.game,'Smith',self)
        new_state.enter_state()

class MrMine(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = ['reindeer']#priority events to say
        self.event = []#normal events to say
        self.quest = []#quest stuff to say

class MrCarpenter(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = []#priority events to say
        self.event = []#normal events to say
        self.quest = []#quest stuff to say

class MrBanks(NPC):#bank
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.ammount = 0

    def buisness(self):#enters after conversation
        new_state = states.Facilities(self.game_objects.game,'Bank',self)
        new_state.enter_state()

class MsButterfly(NPC):#lumber jack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        self.game_objects.quests_events.initiate_quest('fragile_butterfly')
        self.game_objects.player.inventory['pixie dust'] = 1

class MrWood(NPC):#lumber jack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = []#priority events to say
        self.event = []#normal events to say
        self.quest = ['lumberjack_omamori']#quest stuff to say

    def interact(self):#when plater press t
        new_state = states.Conversation(self.game_objects.game, self)
        new_state.enter_state()
        if self.game_objects.world_state.quests.get('lumberjack_omamori', False):#if the quest is running
            self.game_objects.quests_events.active_quests['lumberjack_omamori'].complete()

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 10
        self.health_bar = Health_bar(self)

    def dead(self):#called when death animation is finished
        self.loots()
        self.give_abillity()
        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.update_event(str(type(self).__name__).lower())
        new_game_state = states.Blit_image_text(self.game_objects.game, self.game_objects.player.sprites[self.ability][0],self.ability)
        new_game_state.enter_state()
        new_game_state = states.Defeated_boss(self.game_objects.game)
        new_game_state.enter_state()

    def health_bar(self):#called from omamori Boss_HP
        self.health_bar.max_health = self.health
        self.game_objects.cosmetics.add(self.health_bar)

    def give_abillity(self):
        self.game_objects.player.abilities.spirit_abilities[self.ability] = getattr(sys.modules[__name__], self.ability)(self.game_objects.player)

    def knock_back(self,dir):
        pass

    def take_dmg(self,dmg):
        super().take_dmg(dmg)
        #self.health_bar.resize()

class Reindeer(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/enteties/boss/reindeer/',game_objects)
        self.image = self.sprites['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate = states_reindeer.Idle(self)
        AI_reindeer.build_tree(self)

        self.ability = 'air_dash_main'#the stae of image that will be blitted to show which ability that was gained
        self.attack = Sword
        self.special_attack = Horn_vines
        self.attack_distance = [50,10]

    def give_abillity(self):#called when reindeer dies
        self.game_objects.player.states['Dash'] = True#append dash abillity to available states

class Butterfly(Flying_enemy):
    def __init__(self, pos, game_objects, quest = None):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/boss/butterfly/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos,self.image.size)
        self.hitbox = self.rect.copy()
        self.AI = AI_butterfly.Idle(self)
        self.currentstate = states_butterfly.Idle(self)
        self.health =20
        self.quest = quest

    def knock_back(self,dir):
        pass

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        self.quest.incrase_kill()
        super().dead()

    def right_collision(self,block):
        pass

    def left_collision(self,block):
        pass

    def down_collision(self,block):
        pass

    def top_collision(self,block):
        pass

class Rhoutta_encounter(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/enteties/boss/rhoutta/',game_objects)
        self.image = self.sprites['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 3
        self.attack_distance = [100,10]
        self.attack = Sword
        self.dmg = 0

    def dead(self):
        self.game_objects.game.state_stack[-1].exit_state()
        self.game_objects.player.reset_movement()
        new_game_state = states.Cutscenes(self.game_objects.game,'Rhoutta_encounter')
        new_game_state.enter_state()

#stuff
class Timer_display(Staticentity):#to display a timer on screen
    def __init__(self, entity, time):
        super().__init__([0,0], entity.game_objects)
        self.entity = entity
        self.time = time

    def update(self):
        self.time -= self.game_objects.game.dt
        if self.time < 0:
            self.entity.time_out()
            self.kill()

    def draw(self, target):
        string = str(round(self.time / 60, 2))#seconds¨
        size = (50,12)
        image = self.game_objects.font.render(size, string + ' seconds')
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(image, target, position = [self.game_objects.game.window_size[0] * 0.5 - size[0], self.game_objects.game.window_size[1] * 0.2], scale = [3,3], shader = self.game_objects.shaders['colour'])#shader render
        image.release()

    def release_texture(self):
        pass

class Camera_Stop(Staticentity):
    def __init__(self, game_objects, size, pos, dir, offset):
        super().__init__(pos, game_objects)
        self.hitbox = self.rect.inflate(0,0)
        self.size = size
        self.rect[2] = size[0]
        self.rect[3] = size[1]
        self.offset = int(offset)#number of tiles in the "negative direction" in which the stop should apply
        self.currentstate = getattr(states_camerastop, 'Idle_' + dir)(self)

    def release_texture(self):#called when .kill() and empty group
        pass

    def update(self):
        self.currentstate.update()

class Spawner(Staticentity):#an entity spawner
    def __init__(self,pos,game_objects,values):
        super().__init__(pos, game_objects)
        self.entity = values['entity']
        self.number = int(values['number'])
        self.spawn_entities()

    def spawn_entities(self):
        for i in range(0,self.number):
            offset=random.randint(-100, 100)
            pos=[self.rect.x+offset,self.rect.y]
            obj=getattr(sys.modules[__name__], self.entity)(pos,self.game_objects)
            self.game_objects.enemies.add(obj)

class Fade_effect(Staticentity):#fade effect
    def __init__(self, entity, alpha = 255):
        super().__init__(entity.rect.center,entity.game_objects)
        self.image = entity.image
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.center = entity.rect.center
        self.alpha = alpha

        self.shader = entity.game_objects.shaders['alpha']
        self.shader['alpha'] = alpha
        self.true_pos = self.rect.topleft
        self.dir = entity.dir.copy()

    def update(self):
        self.alpha *= 0.95
        self.destroy()

    def draw(self, target):
        self.shader['alpha'] = self.alpha
        super().draw(target)

    def destroy(self):
        if self.alpha < 5:
            self.kill()

    def release_texture(self):#don't release it becase it seems like it is conencted in memoery to player
        pass

class Sign_symbols(Staticentity):#a part of sign, it blits the landsmarks in the appropriate directions
    def __init__(self, entity):
        super().__init__(entity.rect.center,entity.game_objects)
        self.game_objects = entity.game_objects
        self.image = self.game_objects.game.display.make_layer(entity.game_objects.game.window_size)#TODO
        self.rect = pygame.Rect(0, 0, self.image.texture.width, self.image.texture.height)
        self.rect.center = [entity.game_objects.game.window_size[0]*0.5,entity.game_objects.game.window_size[0]*0.5-100]
        self.image.clear(0,0,0,255)

        dir = {'left':[self.image.texture.width*0.25,150],'up':[self.image.texture.width*0.5,50],'right':[self.image.texture.width*0.75,150],'down':[self.image.texture.width*0.5,300]}
        for key in entity.directions.keys():
            text = self.game_objects.font.render((30,12), entity.directions[key])
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(text, self.image, position = dir[key],shader = self.game_objects.shaders['colour'])#shader render
            text.release()

        self.render_fade = [self.render_in, self.render_out]
        self.init()

    def init(self):
        self.fade = 0
        self.page = 0

    def update(self):
        self.render_fade[self.page]()

    def draw(self, target):
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['alpha'])#shader render

    def render_in(self):
        self.fade += self.game_objects.game.dt
        self.fade = min(self.fade,200)
        self.game_objects.shaders['alpha']['alpha'] = self.fade

    def render_out(self):
        self.fade -= self.game_objects.game.dt
        self.fade = max(self.fade,0)
        self.game_objects.shaders['alpha']['alpha'] = self.fade

        if self.fade < 10:
            self.init()
            self.kill()

    def finish(self):#called when fading out should start
        self.page = 1

    def release_texture(self):
        pass

class Shade_Screen(Staticentity):#a screen that can be put on each layer to make it e.g. dark or light
    def __init__(self, game_objects, parallax, colour):
        super().__init__([0,0],game_objects)
        if parallax[0] == 1: self.colour = (colour.g, colour.b, colour.a, 0)
        else: self.colour = (colour.g,colour.b,colour.a,15/parallax[0])

        self.shader_state = states_shader.Idle(self)

        layer1 = self.game_objects.game.display.make_layer(game_objects.game.window_size)#make an empty later
        layer1.clear(self.colour)
        self.image = layer1.texture#get the texture of the layer

    def release_texture(self):
        self.image.release()

    def update(self):
        self.true_pos = [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]#this is [0,0]
        self.shader_state.update()

    def draw(self, target):
        self.shader_state.draw()
        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render

#Player movement abilities, handles them. Contains also spirit abilities
class Player_abilities():
    def __init__(self,entity):
        self.entity = entity
        self.spirit_abilities = {'Thunder': Horagalles_rage(entity),'Shield': Tjasolmais_embrace(entity),'Bow': Juksakkas_blessing(entity),'Migawari': Maderakkas_reflection(entity),'Slow_motion': Beaivis_time(entity)}#abilities aila has
        self.equip = 'Thunder'#spirit ability pointer
        self.movement_dict = {'Dash':Dash(entity),'Wall_glide':Wall_glide(entity),'Double_jump':Double_jump(entity)}#abilities the player has
        self.movement_abilities = list(self.movement_dict.values())#make it a list
        self.number = 3#number of movement abilities one can have equiped, the equiped one will be appended to self.entity.states

    def remove_ability(self):#movement stuff
        abilities = self.movement_abilities[0:self.number]#the abilities currently equiped
        for ability in abilities:#remove ability
            string = ability.__class__.__name__
            self.entity.states.remove(string)

    def add_ability(self):#movement stuff
        abilities = self.movement_abilities[0:self.number]#the abilities to be equiped
        for ability in abilities:#at tthe ones we have equipped
            string = ability.__class__.__name__
            self.entity.states.add(string)

    def increase_number(self):#movement stuff
        self.number += 1
        self.number = min(self.number,3)#limit the number of abilities one can equip at the same time

    def handle_input(self,input):#movement stuff
        value = input[2]['d_pad']
        if sum(value) == 0: return#if d_pad wasn't pressed

        if value[0] == 1:#pressed right
            self.remove_ability()
            self.movement_abilities = self.movement_abilities[-1:] + self.movement_abilities[:-1]#rotate the abilityes to the right
            self.entity.game_objects.UI['gameplay'].init_ability()
            self.add_ability()
        elif value[0] == -1:#pressed left
            self.remove_ability()
            self.movement_abilities = self.movement_abilities[1:] + self.movement_abilities[:1]#rotate the abilityes to the left
            self.entity.game_objects.UI['gameplay'].init_ability()
            self.add_ability()
        elif value[1] == 1:#pressed up
            pass
        elif value[1] == -1:#pressed down
            pass

class Movement_abilities():#ailas movement abilities. Contains logic to handle the level ups from save point. Should it do something when used?
    def __init__(self,entity):
        self.entity = entity
        self.level = 1

    def upgrade_ability(self):
        self.level += 1

class Dash(Movement_abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Wall_glide(Movement_abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Double_jump(Movement_abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Omamoris():#omamori handler -> "neckalce"
    def __init__(self,entity):
        self.entity = entity
        self.equipped = {'0':[],'1':[],'2':[]}#equiped omamoris
        self.inventory = {}#omamoris in inventory.: 'Half_dmg':Half_dmg([0,0], entity.game_objects, entity),'Loot_magnet':Loot_magnet([0,0], entity.game_objects, entity),'Boss_HP':Boss_HP([0,0], entity.game_objects, entity)
        entity.dmg_scale = 1#one omamori can make it 0.5 (take half the damage)
        self.level = 1#can be leveld up at black smith

    def level_up(self):#shuold be called from black smith. bot implement yet
        self.level += 1

    def update(self):
        for omamoris in self.equipped.values():
            for omamori in omamoris:
                omamori.equipped()

    def handle_input(self,input):
        for omamoris in self.equipped.values():
            for omamori in omamoris:
                omamori.handle_input(input)

    def equip_omamori(self, omamori_string, list_of_places):
        new_omamori = getattr(sys.modules[__name__], omamori_string)([0,0], self.entity.game_objects, entity = self.entity)

        if self.inventory[omamori_string].state != 'equip':#if not alrady equiped
            number_equipped = len(self.equipped['0']) + len(self.equipped['1']) + len(self.equipped['2'])
            if number_equipped >= 7: return [False, 'no avilable slots']

            if new_omamori.level == 2:
                if self.level == 0: return [False, 'no avilable slots']
                if len(self.equipped['2']) != 0: return [False, 'no avilable slots']

                self.inventory[omamori_string].currentstate.set_animation_name('equip')
                new_omamori.attach()
                new_omamori.set_pos(list_of_places[-1].rect.topleft)
                self.equipped['2'].append(new_omamori)

            elif new_omamori.level == 1:
                if len(self.equipped['1']) + len(self.equipped['2']) >= self.level: return [False, 'no avilable slots']

                self.inventory[omamori_string].currentstate.set_animation_name('equip')
                new_omamori.attach()
                new_omamori.set_pos(list_of_places[7 - self.level + len(self.equipped['1'])].rect.topleft)
                if 7 - self.level + len(self.equipped['1']) == 6:
                    self.equipped['2'].append(new_omamori)
                else:
                    self.equipped['1'].append(new_omamori)

            elif new_omamori.level == 0:
                self.inventory[omamori_string].currentstate.set_animation_name('equip')
                new_omamori.attach()
                new_omamori.set_pos(list_of_places[len(self.equipped['0'])].rect.topleft)
                self.equipped['0'].append(new_omamori)

        else:# If already equipped, remove the omamori
            self.inventory[omamori_string].currentstate.set_animation_name('idle')
            self.inventory[omamori_string].ui_group.empty()

            for key in self.equipped.keys():
                for omamori in self.equipped[key]:
                    if type(omamori).__name__ != omamori_string: continue
                    omamori.detach()
                    self.equipped[key].remove(omamori)
                    break

        return [True]

#projectiles
class Projectiles(Platform_entity):#projectiels
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.timers = []#a list where timers are append whe applicable, e.g. jump, invincibility etc.
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}
        self.lifetime = kwarg.get('lifetime', 300)

    def update(self):
        super().update()
        self.update_timers()
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    #collisions
    def collision_platform(self, collision_plat):#collision platform
        collision_plat.take_dmg(self)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        eprojectile.take_dmg(self.dmg)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        collision_enemy.take_dmg(self.dmg)

    def collision_inetractables(self,interactable):#collusion interactables
        pass

    def countered(self,dir, pos):#called from sword collsion with purple infinity stone equipped
        pass

    def take_dmg(self, dmg):
        pass

    #pltform, ramp collisions.
    def ramp_top_collision(self, position):#called from collusion in clollision_ramp
        pass

    def ramp_down_collision(self, position):#called from collusion in clollision_ramp
        pass

    def right_collision(self, block):
        self.collision_platform(block)

    def left_collision(self, block):
        self.collision_platform(block)

    def down_collision(self, block):
        self.collision_platform(block)

    def top_collision(self, block):
        self.collision_platform(block)

    def limit_y(self):#limits the velocity on ground, onewayup. But not on ramps: it makes a smooth drop
        pass

    def release_texture(self):#i guess all projectiles will have a pool
        pass

class Bouncy_balls(Projectiles):#for ball challange room
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Bouncy_balls.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.light = game_objects.lights.add_light(self)
        self.velocity = [random.uniform(-10,10),random.uniform(-10,-4)]

        self.quest = kwarg.get('quest', None)

    def pool(game_objects):
        Bouncy_balls.sprites = read_files.load_sprites_dict('Sprites/attack/projectile_1/',game_objects)

    def release_texture(self):
        pass

    def kill(self):#when lifeitme runs out or hit by aila sword
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    def aila_sword(self):#when hit by aila sword without purple stone
        self.velocity = [0,0]
        self.dmg = 0
        self.currentstate.handle_input('Death')
        if self.quest: self.quest.increase_kill()

    #platform collisions
    def right_collision(self, block):
        self.hitbox.right = block.hitbox.left
        self.collision_types['right'] = True
        self.currentstate.handle_input('Wall')
        self.velocity[0] = -self.velocity[0]

    def left_collision(self,hitbox):
        self.hitbox.left = block.hitbox.right
        self.collision_types['left'] = True
        self.currentstate.handle_input('Wall')
        self.velocity[0] = -self.velocity[0]

    def top_collision(self,hitbox):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def down_collision(self,hitbox):
        self.hitbox.bottom = block.hitbox.top
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1

class Poisoncloud(Projectiles):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Poisoncloud.sprites
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.dmg = 1
        self.lifetime=400

    def pool(game_objects):
        Poisoncloud.sprites = read_files.load_sprites_dict('Sprites/attack/poisoncloud/',game_objects)

    def collision_ene(self,collision_ene):
        pass

    def destroy(self):
        if self.lifetime<0:
            self.currentstate.handle_input('Death')

    def countered(self,dir,pos):#shielded
        self.currentstate.handle_input('Death')

class Poisonblobb(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = Poisonblobb.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 100)
        self.dir = kwarg.get('dir', [1,0])
        self.velocity = [self.dir[0]*5,-1]

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        self.velocity[1] += 0.1*self.game_objects.game.dt*self.slow_motion#graivity

    def take_dmg(self, dmg):#aila sword without purple stone
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def collision_platform(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def pool(game_objects):
        Poisonblobb.sprites = read_files.load_sprites_dict('Sprites/attack/poisonblobb/', game_objects)

class Projectile_1(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = Projectile_1.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 200)
        self.dir = kwarg.get('dir', [1, 0])
        amp = kwarg.get('amp', [5, 0])
        self.velocity = [-amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def pool(game_objects):
        Projectile_1.sprites = read_files.load_sprites_dict('Sprites/attack/projectile_1/',game_objects)

    def collision_platform(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def ramp_top_collision(self, position):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def ramp_down_collision(self, position):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def countered(self, dir, pos):#called from sword collsion with purple infinity stone
        dy = self.rect.centery - pos[1]
        dx = self.rect.centerx - pos[0]

        self.velocity[0] = 300/dx
        self.velocity[1] = 0

class Falling_rock(Projectiles):#things that can be placed in cave, the source makes this and can hurt player
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Falling_rock.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.dmg = 1
        self.currentstate = states_droplets.Idle(self)

    def pool(game_objects):
        Falling_rock.sprites = read_files.load_sprites_dict('Sprites/animations/falling_rock/rock/', game_objects)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        super().collision_enemy(collision_enemy)
        self.currentstate.handle_input('death')

    def collision_platform(self, collision_plat):#collision platform, called from collusoin_block
        super().collision_platform(collision_plat)
        self.currentstate.handle_input('death')

class Droplet(Projectiles):#droplet that can be placed, the source makes this and can hurt player
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Droplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.currentstate = states_droplets.Idle(self)

        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            self.dmg = 1#acid
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more
        else:
            self.dmg = 0#water
            self.shader_state = states_shader.Idle(self)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_enemy(collision_enemy)

    def collision_platform(self, collision_plat):#collision platform
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_platform(collision_plat)

    def pool(game_objects):
        Droplet.sprites = read_files.load_sprites_dict('Sprites/animations/droplet/droplet/', game_objects)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)

class Horn_vines(Projectiles):#the reindeer attack
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Horn_vines.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],0,0)#
        self.currentstate = states_horn_vines.Idle(self)#
        self.dmg = 1
        self.lifetime = 500

    def pool(game_objects):
        Horn_vines.sprites = read_files.load_sprites_dict('Sprites/attack/horn_vines/',game_objects)

    def destroy(self):
        if self.lifetime < 0:
            self.entity.currentstate.handle_input('Horn_vines')
            self.kill()

class Melee(Projectiles):
    def __init__(self, entity):
        super().__init__([0,0], entity.game_objects)
        self.entity = entity#needs entity for making the hitbox follow the player in update hitbox
        self.dir = entity.dir.copy()
        self.direction_mapping = {(0, 0): ('center', 'center'), (1, 1): ('midbottom', 'midtop'),(-1, 1): ('midbottom', 'midtop'), (1, -1): ('midtop', 'midbottom'),(-1, -1): ('midtop', 'midbottom'),(1, 0): ('midleft', 'midright'),(-1, 0): ('midright', 'midleft')}

    def update_hitbox(self):#cannpt not call in update becasue aila moves after the update call (because of the collision)
        rounded_dir = (sign(self.dir[0]), sign(self.dir[1]))#analogue controls may have none integer values
        hitbox_attr, entity_attr = self.direction_mapping[rounded_dir]
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes

    def countered(self,dir,pos):#called from sword collision_projectile, purple initinty stone
        return
        self.entity.countered()
        self.kill()

    def update_rect_y(self):
        pass

    def update_rect_x(self):
        pass

class Hurt_box(Melee):#a hitbox that spawns
    def __init__(self, entity, size = [64,64], lifetime = 100):
        super().__init__(entity)
        self.hitbox = pygame.Rect(entity.rect.topleft, size)
        self.dir = [0, 0]
        self.lifetime = lifetime
        self.dmg = 1

    def update(self):
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destroy()

    def draw(self, target):
        pass

class Explosion(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = Explosion.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(entity.rect.centerx,entity.rect.centery,self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.dir = [0, 0]
        self.lifetime = 100
        self.dmg = 1

    def pool(game_objects):
        Explosion.sprites = read_files.load_sprites_dict('Sprites/attack/explosion/', game_objects)

    def reset_timer(self):
        self.kill()

class Reflect(Melee):#pressing k
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/hurt_box/',entity.game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = self.entity.hitbox.copy()#pygame.Rect(self.entity.rect[0],self.entity.rect[1],20,40)
        self.hitbox = self.rect.copy()
        self.dmg = 0
        self.lifetime = 25

    def update_hitbox(self):
        if self.dir[0] > 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def collision_enemy(self,collision_enemy):
        collision_enemy.countered()
        self.kill()

    def collision_projectile(self,eprojectile):
        return
        self.entity.projectiles.add(eprojectile)#add the projectilce to Ailas projectile group
        eprojectile.countered(self.dir,self.rect.center)

class Sword(Melee):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()
        self.rect = pygame.Rect(entity.rect.centerx,entity.rect.centery,self.image.width*2,self.image.height*2)
        self.hitbox = self.rect.copy()

    def pool(game_objects):
        Sword.sprites = read_files.load_sprites_dict('Sprites/attack/sword/', game_objects)

    def init(self):
        self.sprites = Sword.sprites
        self.image = self.sprites['idle'][0]
        self.dmg = self.entity.dmg
        self.lifetime = 10

    def collision_enemy(self, collision_enemy):
        self.sword_jump()
        if collision_enemy.invincibile: return
        collision_enemy.take_dmg(self.dmg)
        collision_enemy.knock_back(self.dir)
        collision_enemy.hurt_particles(dir = self.dir)
        #slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])#self.entity.cosmetics.add(slash)
        self.clash_particles(collision_enemy.hitbox.center, lifetime = 20, dir = [random.randint(-180, 180),0])

    def sword_jump(self):
        #print(self.dir[1])
        if math.floor(self.dir[1]) == -1:
            self.entity.velocity[1] = C.pogo_vel

    def clash_particles(self, pos, number_particles = 12, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, **kwarg)
            self.entity.game_objects.cosmetics.add(obj1)

    def collision_inetractables(self,interactable):#called when projectile hits interactables
        interactable.take_dmg(self)#some will call clash_particles but other will not. So sending self to interactables

class Aila_sword(Sword):
    def __init__(self, entity):
        super().__init__(entity)
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.currentstate = states_sword.Slash_1(self)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/aila_sword/')

        self.tungsten_cost = 1#the cost to level up to next level
        self.level = 0#determines how many stone one can attach
        self.equip = []#stone pointers, the ones attached to the sword, strings
        self.stones = {'red':Red_infinity_stone([0,0],entity.game_objects, entity = self),'green':Green_infinity_stone([0,0],entity.game_objects, entity = self),'blue':Blue_infinity_stone([0,0],entity.game_objects, entity = self),'orange':Orange_infinity_stone([0,0],entity.game_objects, entity = self),'purple':Purple_infinity_stone([0,0],entity.game_objects, entity = self)}#the ones aila has picked up
        self.swing = 0#a flag to check which swing we are at (0 or 1)

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/attack/aila_slash/',self.entity.game_objects)
        self.image = self.sprites['slash_1'][0]
        self.dmg = 1

    def destroy(self):
        if self.lifetime < 0:
            self.currentstate.increase_phase()
            self.kill()#removes from projectiles gruop

    def update_hitbox(self):#called from aila's update_hitbox, every frame
        super().update_hitbox()#follows the hitbox of aila depending on the direction
        self.currentstate.update_hitbox()

    def set_stone(self,stone_str):#called from smith
        if len(self.equip) < self.level:
            self.equip.append(stone_str)
            self.stones[stone_str].attach()

    def remove_stone(self):#not impleented
        pass

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with projectile
        if eprojectile.invincibile: return
        eprojectile.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period

        if 'purple' in self.equip:#if the purpuple stone is equped
            eprojectile.countered(self.dir, self.rect.center)
            self.sword_jump()
        else:
            eprojectile.take_dmg(self.dmg)

    def collision_enemy(self, collision_enemy):
        self.sword_jump()
        if collision_enemy.invincibile: return
        collision_enemy.take_dmg(self.dmg)
        collision_enemy.knock_back(self.dir)
        collision_enemy.hurt_particles(dir = self.dir)#, colour=[255,255,255,255])
        self.clash_particles(collision_enemy.hitbox.center)
        self.game_objects.sound.play_sfx(self.sounds['sword_hit_enemy'][0])#should be in states

        #self.game_objects.camera_manager.camera.camera_shake(amp=2,duration=30)#amplitude and duration
        collision_enemy.currentstate.handle_input('sword')
        for stone in self.equip:
            self.stones[stone].collision()#call collision specific for stone

    def clash_particles(self, pos, number_particles=12):
        angle = random.randint(-180, 180)#the erection anglex
        color = [255,255,255,255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos,self.game_objects,distance=0,lifetime=15,vel={'linear':[7,14]},dir=[angle,0],scale=1,colour=color,state = 'Idle')
            self.entity.game_objects.cosmetics.add(obj1)

    def level_up(self):#called when the smith imporoves the sword
        if self.level >= 3: return
        self.entity.inventory['Tungsten'] -= self.tungsten_cost
        self.dmg *= 1.2
        self.level += 1
        self.tungsten_cost += 2#1, 3, 5 tungstes to level upp 1, 2, 3

class Thunder(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Thunder.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.dmg = kwarg.get('dmg', 1)

    def pool(game_objects):
        Thunder.sprites = read_files.load_sprites_dict('Sprites/attack/Thunder/', game_objects)

    def collision_enemy(self,collision_enemy):
        super().collision_enemy(collision_enemy)
        self.dmg = 0
        collision_enemy.velocity = [0,0]#slow him down

    def reset_timer(self):
        self.dmg = 1
        self.kill()

class Arrow(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Arrow.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.dmg = 1
        self.lifetime = 100

        self.dir = kwarg.get('dir', [1,0])
        self.velocity=[self.dir[0] * 20, self.dir[1] * 20]

    def pool(game_objects):
        Arrow.sprites = read_files.load_sprites_dict('Sprites/attack/arrow/', game_objects)

    def collision_enemy(self,collision_enemy):
        collision_enemy.take_dmg(self.dmg)
        self.velocity = [0,0]
        self.kill()

    def collision_platform(self, platform):
        self.velocity = [0,0]
        self.dmg = 0

class Shield(Projectiles):#a protection shield
    def __init__(self, entity, **kwarg):
        super().__init__(entity.hitbox.topleft, entity.game_objects)
        self.entity = entity
        self.image = Shield.image
        self.rect = pygame.Rect(entity.hitbox.centerx, entity.hitbox.centery, self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.time = 0
        self.entity.invincibile = True
        self.health = kwarg.get('health', 1)
        self.general_Timer = General_Timer(self, 100, self.time_out)#how long it will last after taking reaching 0 health

    def take_dmg(self, dmg):#called when entity takes damage
        if self.invincibile: return
        self.health -= dmg
        self.timer_jobs['invincibility'].activate()
        #TODO make it red momentary or something to indicate that it too damage
        if self.health < 0:
            self.general_Timer.activate()
            #TODO make it blink or something to indicate that it will die soon

    def time_out(self):#called when general timer it count down
        self.kill()

    def update(self):
        self.update_timers()
        self.time += self.entity.game_objects.game.dt
        self.update_pos()

    def update_pos(self):
        self.true_pos = [int(self.entity.hitbox.center[0] - self.game_objects.camera_manager.camera.scroll[0] - self.image.width*0.5),int(self.entity.hitbox.center[1] - self.game_objects.camera_manager.camera.scroll[1]- self.image.height*0.5)]

    def draw(self, target):
        self.game_objects.shaders['shield']['time'] = self.time*0.1
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = self.hitbox.topleft, shader = self.game_objects.shaders['shield'])#shader render

    def pool(game_objects):
        size = [90, 90]
        Shield.image = game_objects.game.display.make_layer(size).texture

    def kill(self):
        super().kill()
        self.entity.invincibile = False
        self.entity.tjasolmais_embrace = None

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        pass

    def collision_platform(self, collision_plat):#collision platform, called from collusoin_block
        pass

#aila abilities
class Player_ability():#the abilities aila can absorb. Handles upgrades, spawn the ability and UI and stuff
    def __init__(self, entity):
        self.entity = entity
        self.level = 1#upgrade pointer

    def initiate(self):#called when using the ability
        pass

class Horagalles_rage(Player_ability):#desolate dive:thunder god:
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/horagalles_rage/',entity.game_objects)

    def initiate(self, enemy_rect):
        thunder = Thunder(enemy_rect, self.entity.game_objects, lifetime =  1000)
        thunder.rect.midbottom = enemy_rect.midbottom
        thunder.hitbox = thunder.rect.copy()
        self.entity.projectiles.add(thunder)#add attack to group

class Tjasolmais_embrace(Player_ability):#makes the shield, water god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/tjasolmais_embrace/',entity.game_objects)
        #-> higher level can reflect projectiles? or maybe hurt enemy?

    def initiate(self):#called when using the abilty
        shield = Shield(self.entity)
        self.entity.tjasolmais_embrace = shield
        self.entity.projectiles.add(shield)

class Maderakkas_reflection(Player_ability):#migawari: woman/mother god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/maderakkas_reflection/',entity.game_objects)
        self.health = 1

    def initiate(self):#called when using the ability
        spawn = Maderakkas_reflection_entity(self.entity.rect.midtop, self.entity.game_objects, lifetime = 1000, health = self.health)
        self.entity.game_objects.players.add(spawn)

    def upgrade_ability(self):#called from upgrade menu
        self.level += 1
        if self.level == 2:
            self.health = 2

class Beaivis_time(Player_ability):#slow motion -> sun god: Beaiviáigi in sami
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/beaivis_time/',entity.game_objects)
        self.duration = 200#slow motion duration, in time [whatever units]
        self.rate = 0.5#slow motion rate

    def initiate(self):#called when using the ability from player states
        new_state = states.Slow_motion_gameplay(self.entity.game_objects.game, rate = self.rate, duration = self.duration)
        new_state.enter_state()

    def upgrade_ability(self):#called from upgrade menu
        self.level += 1
        if self.level == 3:
            self.entity.slow_motion = 1/self.rate#counteract slowmotion for aila
            self.duration = 400#slow motion duration, in time [whatever units]
        elif self.level == 2:
            self.duration = 400#slow motion duration, in time [whatever units]

class Juksakkas_blessing(Player_ability):#arrow -> fetillity god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/juksakkas_blessing/', entity.game_objects)
        self.level = 1#upgrade pointer

    def initiate(self):#called when using the attack
        if self.entity.dir[1] == 0:#left or right
            dir = self.entity.dir.copy()
        else:#up or down
            dir = [0,-self.entity.dir[1]]

        self.entity.projectiles.add(Arrow(pos = self.entity.hitbox.topleft, game_objects = self.entity.game_objects, dir = dir))

#things player can pickup
class Loot(Platform_entity):#
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.description = ''
        self.bounce_coefficient = 0.6

    def update_vel(self):#add gravity
        self.velocity[1] += 0.3*self.game_objects.game.dt*self.slow_motion

    def update(self):
        super().update()
        self.update_vel()

    def attract(self, pos):#the omamori calls on this in loot group
        pass

    def interact(self, player):#when player press T
        pass

    def player_collision(self, player):#when the player collides with this object
        pass

    def release_texture(self):#stuff that have pool shuold call this
        pass

    #plotfprm collisions
    def top_collision(self,block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def down_collision(self,block):
        super().down_collision(block)
        self.velocity[0] = 0.5 * self.velocity[0]
        self.velocity[1] = -self.bounce_coefficient*self.velocity[1]
        self.bounce_coefficient *= self.bounce_coefficient

    def right_collision(self,block):
        super().right_collision(block)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self,block):
        super().left_collision(block)
        self.velocity[0] = -self.velocity[0]

    def limit_y(self):
        if self.bounce_coefficient < 0.1:#to avoid falling through one way collisiosn
            self.velocity[1] = max(self.velocity[1],0.6)

class Heart_container(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/items/heart_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'A heart container'

    def update_vel(self):
        self.velocity[1] = 3*self.game_objects.game.dt*self.slow_motion

    def player_collision(self, player):
        player.max_health += 1
        #a cutscene?
        self.kill()

class Spirit_container(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/items/spirit_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'A spirit container'

    def update_vel(self):
        self.velocity[1]=3*self.game_objects.game.dt*self.slow_motion

    def player_collision(self,player):
        player.max_spirit += 1
        #a cutscene?
        self.kill()

class Soul_essence(Loot):#genkidama
    def __init__(self, pos, game_objects, ID_key = None):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/items/soul_essence/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'An essence container'#for shops
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def player_collision(self, player):
        player.inventory['Soul_essence'] += 1
        self.game_objects.world_state.state[self.game_objects.map.level_name]['soul_essence'][self.ID_key] = True#write in the state file that this has been picked up
        #make a cutscene?TODO
        self.kill()

    def update(self):
        super().update()
        obj1 = getattr(particles, 'Spark')(self.rect.center, self.game_objects, distance = 100, lifetime=20, vel={'linear':[2,4]}, fade_scale = 10)
        self.game_objects.cosmetics.add(obj1)

    def update_vel(self):
        pass

class Spiritorb(Loot):#the thing that gives spirit
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/items/spiritorbs/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def player_collision(self, player):
        player.add_spirit(1)
        self.kill()

    def update_vel(self):
        pass

class Enemy_drop(Loot):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.lifetime = 500
        self.velocity = [random.uniform(-3, 3),-3]

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destory()

    def attract(self,pos):#the omamori calls on this in loot group
        if self.lifetime < 350:
            self.velocity = [0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def player_collision(self, player):#when the player collides with this object
        if self.currentstate.__class__.__name__ == 'Death': return#enter only once
        self.game_objects.sound.play_sfx(self.sounds['death'][0])#should be in states
        obj = (self.__class__.__name__)#get the string in question
        if player.inventory.get(obj, False):#not the first time
          self.game_objects.player.inventory[obj] += 1
        else: #first time
            self.game_objects.player.inventory[obj] = 1
        self.currentstate.handle_input('Death')

class Amber_Droplet(Enemy_drop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Amber_Droplet.sprites
        self.sounds = Amber_Droplet.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.hitbox = pygame.Rect(0,0,16,16)
        self.hitbox.center = pos
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'moneyy'

    def player_collision(self,player):#when the player collides with this object
        super().player_collision(player)
        self.game_objects.world_state.update_statistcis('amber_droplet')

    def pool(game_objects):#all things that should be saved in object pool
        Amber_Droplet.sprites = read_files.load_sprites_dict('Sprites/enteties/items/amber_droplet/',game_objects)
        Amber_Droplet.sounds = read_files.load_sounds_dict('audio/SFX/enteties/items/amber_droplet/')

class Bone(Enemy_drop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Bone.sprites
        self.sounds = Bone.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.hitbox = pygame.Rect(0,0,16,16)
        self.hitbox.center = pos
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'Ribs from my daugther. You can respawn and stuff'

    def use_item(self):
        if self.game_objects.player.inventory['Bone'] <= 0: return#if we don't have bones
        self.game_objects.player.inventory['Bone'] -= 1
        self.game_objects.player.spawn_point['bone'] = {'map':self.game_objects.map.level_name, 'point':self.game_objects.camera_manager.camera.scroll}
        self.game_objects.player.currentstate.enter_state('Plant_bone_main')

    def pool(game_objects):#all things that should be saved in object pool
        Bone.sprites = read_files.load_sprites_dict('Sprites/enteties/items/bone/',game_objects)
        Bone.sounds = read_files.load_sounds_dict('audio/SFX/enteties/items/bone/')

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Heal_item(Enemy_drop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Heal_item.sprites
        self.sounds = Heal_item.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.hitbox = pygame.Rect(0,0,16,16)
        self.hitbox.center = pos
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'Use it to heal'

    def use_item(self):
        if self.game_objects.player.inventory['Heal_item'] < 0: return
        self.game_objects.player.inventory['Heal_item'] -= 1
        self.game_objects.player.heal(1)

    def pool(game_objects):#all things that should be saved in object pool: #obj = cls.__new__(cls)#creatate without runing initmethod
        Heal_item.sprites = read_files.load_sprites_dict('Sprites/enteties/items/heal_item/',game_objects)
        Heal_item.sounds = read_files.load_sounds_dict('audio/SFX/enteties/items/heal_item/')

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Interactable_item(Loot):#need to press Y to pick up - #key items: need to pick up instead of just colliding
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.quest = kwarg.get('quest', None)#quests can be initated when they are picked up
        if not kwarg.get('entity', None):#if it is spawn in the wild
            velocity = kwarg.get('velocity', [2, -4])
            velocity_range = kwarg.get('velocity_range', [1, 0])#olus minus the velocity
            self.velocity = [random.uniform(velocity[0] - velocity_range[0], velocity[0] + velocity_range[0]),random.uniform(velocity[1] - velocity_range[1], velocity[1] + velocity_range[1])]
            self.hitbox = pygame.Rect([pos[0], pos[1]],(16,16))#light need hitbox
            self.light = self.game_objects.lights.add_light(self, radius = 50)
            self.state = 'wild'

    def update(self):
        super().update()
        self.twinkle()

    def pickup(self, player):
        self.game_objects.world_state.state[self.game_objects.map.level_name]['interactable_items'][type(self).__name__] = True#save in state file that the items on this map has picked up (assume that only one interactable item on each room)

    def twinkle(self):
        pos = [self.hitbox.centerx + random.randint(-50, 50), self.hitbox.centery + random.randint(-50, 50)]
        twinkle = Twinkle(pos, self.game_objects)#twinkle.animation.frame = random.randint(0, len(twinkle.sprites['idle']) - 1)
        self.game_objects.cosmetics.add(twinkle)

    def interact(self, player):#when player press T
        player.currentstate.enter_state('Pray_pre')
        if self.quest: self.game_objects.quests_events.initiate_quest(self.quest, item = self)
        self.pickup(player)#object specific
        new_game_state = states.Blit_image_text(self.game_objects.game, self.sprites['idle'][0], self.description)
        new_game_state.enter_state()
        self.kill()

    def kill(self):
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites['wild'] = read_files.load_sprites_list('Sprites/enteties/items/interactables_items/',game_objects)#the sprite to render when they are in the wild

class Tungsten(Interactable_item):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Tungsten.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.description = 'A heavy rock'

    def pickup(self, player):
        super().pickup(player)
        player.inventory['Tungsten'] += 1

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/items/tungsten/',game_objects)
        super().pool(game_objects)

class Omamori(Interactable_item):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.entity = kwarg.get('entity', None)
        self.description = ''#for inventory
        self.ui_group = groups.Group()#for the particle stuff in UI
        self.level = 0

    def equipped(self):#an updated that should be called when equppied
        pass

    def render_UI(self, target):#called from oamori menu
        if self.state != 'equip': return
        obj1 = particles.Floaty_particles(self.rect.center, self.game_objects, distance = 0, vel = {'linear':[0.1,1]}, dir = 'isotropic')
        self.ui_group.add(obj1)
        for spr in self.ui_group.sprites():
            spr.update()#the position
            spr.update_uniforms()#the unforms for the draw
            self.game_objects.game.display.render(spr.image, target, position = spr.rect.topleft, shader = spr.shader)

    def pickup(self, player):
        super().pickup(player)
        player.omamoris.inventory[type(self).__name__] = self
        self.entity = player

    def handle_input(self,input):
        pass

    def detach(self):
        self.currentstate.set_animation_name('idle')

    def attach(self):
        self.currentstate.set_animation_name('equip')

    def reset_timer(self):
        pass

    def set_pos(self,pos):#for inventory
        self.rect.topleft = pos

class Half_dmg(Omamori):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Half_dmg.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.level = 1
        self.description = 'Take half dmg ' + '[' + str(self.level) + ']'

    def attach(self):
        super().attach()
        self.entity.dmg_scale = 0.5

    def detach(self):
        super().detach()
        self.entity.dmg_scale = 1

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/omamori/half_dmg/',game_objects)#for inventory
        super().pool(game_objects)

class Loot_magnet(Omamori):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Loot_magnet.sprites
        self.image = self.sprites[self.state][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.description = 'Attracts loot ' + '[' + str(self.level) + ']'

    def equipped(self):#an update that should be called when equppied
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/omamori/loot_magnet/',game_objects)#for inventory
        super().pool(game_objects)

class Boss_HP(Omamori):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Boss_HP.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.level=2
        self.description = 'Visible boss HP ' + '[' + str(self.level) + ']'

    def attach(self):
        super().attach()
        for enemy in self.entity.game_objects.enemies.sprites():
            enemy.health_bar()#attached a healthbar on boss

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/omamori/boss_HP/',game_objects)#for inventor
        super().pool(game_objects)

class Infinity_stones(Interactable_item):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sword = kwarg.get('entity', None)
        self.description = ''

    def set_pos(self, pos):#for inventory
        self.rect.center = pos

    def reset_timer(self):
        pass

    def attach(self):#called from sword when balcksmith attached the stone
        pass

    def detach(self):
        pass

    def collision(self):#hit enemy
        pass

    def slash(self):#called when swingin sword
        pass

    def pickup(self, player):
        super().pickup(player)
        player.sword.stones[list(self.colour.keys())[0]] = self
        self.sword = player.sword

class Red_infinity_stone(Infinity_stones):#more dmg
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Red_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'red':[255,64,64,255]}
        self.description = '10 procent more damage'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/items/infinity_stones/red/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self):
        self.sword.dmg*=1.1

    def detach(self):
        self.sword.dmg*=(1/1.1)

class Green_infinity_stone(Infinity_stones):#faster slash (changing framerate)
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Green_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'green':[105,139,105,255]}
        self.description = 'fast sword swings'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/items/infinity_stones/green/',game_objects)#for inventory
        super().pool(game_objects)

    def slash(self):
        self.sword.entity.animation.framerate = 0.33

class Blue_infinity_stone(Infinity_stones):#get spirit at collision
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Blue_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'blue':[0,0,205,255]}
        self.description = 'add spirit to the swinger'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/items/infinity_stones/blue/',game_objects)#for inventory
        super().pool(game_objects)

    def collision(self):
        self.sword.entity.add_spirit()

class Orange_infinity_stone(Infinity_stones):#bigger hitbox
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Orange_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'orange':[255,127,36,255]}
        self.description = 'larger hitbox'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/items/infinity_stones/orange/',game_objects)#for inventory
        super().pool(game_objects)

    def detach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y,40,40)
        self.sword.hitbox = self.sword.rect.copy()

    def attach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y,80,40)
        self.sword.hitbox = self.sword.rect.copy()

class Purple_infinity_stone(Infinity_stones):#reflect projectile -> crystal caves
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Purple_infinity_stone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'purple':[154,50,205,255]}
        self.description = 'reflects projectiels'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('Sprites/enteties/items/infinity_stones/purple/',game_objects)#for inventory
        super().pool(game_objects)

#cosmetics
class Blood(Animatedentity):
    def __init__(self, pos, game_objects, dir = [1,0]):
        super().__init__(pos, game_objects)
        self.sprites = Blood.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.dir = dir
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Blood.sprites = read_files.load_sprites_dict('Sprites/GFX/blood/death/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Water_running_particles(Animatedentity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Water_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Water_running_particles.sprites = read_files.load_sprites_dict('Sprites/animations/running_particles/water/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Grass_running_particles(Animatedentity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Grass_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Grass_running_particles.sprites = read_files.load_sprites_dict('Sprites/animations/running_particles/grass/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Dust_running_particles(Animatedentity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Dust_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Dust_running_particles.sprites = read_files.load_sprites_dict('Sprites/animations/running_particles/dust/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Player_Soul(Animatedentity):#the thing that popps out when player dies
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Player_Soul.sprites
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name='once')

        self.timer = 0
        self.velocity = [0,0]

    def pool(game_objects):
        Player_Soul.sprites = read_files.load_sprites_dict('Sprites/enteties/soul/', game_objects)

    def update(self):
        super().update()
        self.update_pos()
        self.timer += self.game_objects.game.dt*self.slow_motion
        if self.timer > 100:#fly to sky
            self.velocity[1] = -20
        elif self.timer>200:
            self.kill()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0], self.true_pos[1] + self.velocity[1]]
        self.rect.topleft = self.true_pos

    def release_texture(self):
        pass

class Spawneffect(Animatedentity):#the thing that crets when aila re-spawns
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/GFX/spawneffect/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.finish = False#needed for the cutscene

    def reset_timer(self):
        self.finish = True
        self.kill()

class Slash(Animatedentity):#thing that pop ups when take dmg or give dmg: GFX
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Slash.sprites
        state = str(random.randint(1, 3))
        self.currentstate.set_animation_name('slash_' + state)
        self.image = self.sprites['slash_' + state][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = pos

    def pool(game_objects):#all things that should be saved in object pool
        Slash.sprites = read_files.load_sprites_dict('Sprites/GFX/slash/',game_objects)

    def reset_timer(self):
        self.kill()

    def release_texture(self):#stuff that have pool shuold call this
        pass

class Rune_symbol(Animatedentity):#the stuff that will be blitted on uberrunestone
    def __init__(self,pos,game_objects,ID_key):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/rune_symbol/' + ID_key + '/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def reset_timer(self):
        pass

class Thunder_aura(Animatedentity):#the auro around aila when doing the thunder attack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/thunder_aura/',game_objects)
        self.currentstate = states_basic.Once(self,next_state = 'Idle',animation_name='idle')#
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()#pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)

    def update(self):
        super().update()
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.inflate_ip(3,3)#the speed should match the animation
        self.hitbox[2]=min(self.hitbox[2],self.rect[2])
        self.hitbox[3]=min(self.hitbox[3],self.rect[3])

    def reset_timer(self):#called when animation is finished
        super().reset_timer()
        self.currentstate.handle_input('Idle')

class Pray_effect(Animatedentity):#the thing when aila pray
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Pray_effect.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def pool(game_objects):
        Pray_effect.sprites = read_files.load_sprites_dict('Sprites/animations/pray_effect/', game_objects)

    def spawn(self):
        pass

    def reset_timer(self):
        self.kill()

    def release_texture(self):
        pass

class Health_bar(Animatedentity):
    def __init__(self,entity):
        super().__init__(entity.rect.center,entity.game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/health_bar/',entity.game_objects)
        self.entity = entity#the boss
        self.max_health = entity.health
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.width = self.rect[2]
        self.rect.topleft = [self.game_objects.game.window_size[0]*0.5 - self.width*0.5,3]

    def resize(self):#in principle, should just be called when boss take dmg
        width = max(self.width * (self.entity.health/self.max_health),0)
        for index, sprite in  enumerate(self.sprites['idle']):
            self.sprites['idle'][index] = pygame.transform.scale(sprite,[width,self.rect[3]])

class Logo_loading(Animatedentity):
    def __init__(self, game_objects):
        super().__init__([500,300], game_objects)
        self.sprites = Logo_loading.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.animation.framerate = 0.1#makes it slower

    def pool(game_objects):
        Logo_loading.sprites = read_files.load_sprites_dict('Sprites/UI/logo_loading/',game_objects)

    def update(self):
        super().update()
        self.rect.topleft = [self.true_pos[0] + self.game_objects.camera_manager.camera.scroll[0], self.true_pos[1] + self.game_objects.camera_manager.camera.scroll[1]]

    def release_texture(self):
        pass

    def reset_timer(self):
        self.kill()

class Twinkle(Animatedentity):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Twinkle.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

    def reset_timer(self):
        super().reset_timer()
        self.kill()

    def release_texture(self):
        pass

    def pool(game_objects):
        Twinkle.sprites = read_files.load_sprites_dict('Sprites/GFX/twinkle/', game_objects)

#interactables
class Interactable(Animatedentity):#interactables
    def __init__(self, pos, game_objects, sfx = None):
        super().__init__(pos, game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft
        if sfx: self.sfx = pygame.mixer.Sound('audio/SFX/environment/' + sfx + '.mp3')
        else: self.sfx = None # make more dynamic incase we want to use more than just mp3

    def update(self):
        super().update()
        self.group_distance()

    def play_sfx(self):
        self.game_objects.sound.play_sfx(self.sfx)

    def interact(self):#when player press T
        pass

    def player_collision(self, player):#player collision
        pass

    def player_noncollision(self):#when player doesn't collide: for grass
        pass

    def take_dmg(self, projectile):#when player hits with e.g. sword
        pass

class Place_holder_interacatble(Interactable):
    def __init__(self,entity, game_objects):
        super().__init__(entity.rect.center, game_objects)
        self.entity = entity
        self.hitbox = entity.hitbox

    def update(self):
        pass

    def draw(self, target):
        pass

    def interact(self):#when player press T
        self.entity.interact()

    def release_texture(self):
        pass

class Bubble_source(Interactable):#the thng that spits out bubbles in cave
    def __init__(self, pos, game_objects, bubble, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/bubble_source/', game_objects)
        self.sounds = read_files.load_sounds_list('audio/SFX/enteties/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()

        self.bubble = bubble#the bubble is in platform, so the reference is sent in init
        self.prop = prop
        self.time = 0

    def group_distance(self):
        pass

    def update(self):
        super().update()
        self.time += 1
        if self.time > 100:
            bubble = self.bubble(self.rect.midtop, self.game_objects, **self.prop)
            self.game_objects.dynamic_platforms.add(bubble)
            self.game_objects.platforms.add(bubble)
            self.time =0

class Challenges(Interactable):#monuments you interact to get quests or challenges
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def render_potrait(self, target):
        pass

    def interact(self):#when plater press t
        if self.interacted: return
        new_state = states.Conversation(self.game_objects.game, self)
        new_state.enter_state()
        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

    def reset(self):#called when challange is failed
        self.shader_state.handle_input('idle')
        self.interacted = False

class Challenge_monument(Challenges):#the status spawning a portal, balls etc - challange rooms
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/challenges/challenge_monument/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.ID = ID
        self.interacted = self.game_objects.world_state.quests.get(ID, False)
        self.dialogue = dialogue.Dialogue_interactable(self, ID)#handles dialoage and what to say

        if self.interacted:
            self.shader_state = states_shader.Tint(self, colour = [0,0,0,100])
        else:
            game_objects.lights.add_light(self)
            self.shader_state = states_shader.Idle(self)

    def buisness(self):#enters after conversation
        self.game_objects.quests_events.initiate_quest(self.ID.capitalize(), monument = self)

class Stone_wood(Challenges):#the stone "statue" to initiate the lumberjacl quest
    def __init__(self, pos, game_objects, quest, item):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/challenges/stone_wood/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.quest = quest
        self.item = item

        self.interacted = self.game_objects.world_state.quests.get(quest, False)
        self.dialogue = dialogue.Dialogue_interactable(self, quest)#handles dialoage and what to say
        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self)

    def buisness(self):#enters after conversation
        item = getattr(sys.modules[__name__], self.item.capitalize())(self.rect.center, self.game_objects, quest = self.quest)#make a class based on the name of the newstate: need to import sys
        self.game_objects.loot.add(item)

class Safe_spawn(Interactable):#area which gives the coordinates which will make aila respawn at after falling into a hole
    def __init__(self, pos, game_objects, size, position):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.position = position

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def player_collision(self, player):
        player.spawn_point['safe_spawn'] = self.position

class Hole(Interactable):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.interacted = False

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def player_collision(self, player):
        if self.interacted: return#enter only once
        self.player_transport(player)
        player.take_dmg(duration = 0)
        self.interacted = True

    def player_transport(self, player):#transports the player to safe position
        if player.health > 1:#if about to die, don't transport to safe point
            new_state = states.Safe_spawn_1(self.game_objects.game)#should be before take_dmg
            new_state.enter_state()
            self.game_objects.player.currentstate.enter_state('Invisible_main')
        else:
            self.game_objects.player.invincibile = False
        player.velocity = [0,0]
        player.acceleration = [0,0]

    def player_noncollision(self):#when player doesn't collide
        self.interacted = False

class Zoom_col(Interactable):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()
        self.rate = kwarg.get('rate', 1)
        self.scale = kwarg.get('scale', 1)
        self.center = kwarg.get('center', (0.5, 0.5))
        self.blur_timer = C.fps

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def player_collision(self, player):
        self.blur_timer -= self.game_objects.game.dt
        if self.blur_timer < 0:
            player.shader_state.handle_input('blur')
            for sprite in self.game_objects.all_bgs:
                if sprite.parallax[0] > 0.8:
                    sprite.blur_radius += (1.1/sprite.parallax[0] - sprite.blur_radius) * 0.06
                    sprite.blur_radius = min(1.1/ sprite.parallax[0], sprite.blur_radius)
                else:
                    sprite.blur_radius -= (sprite.blur_radius - 0.2) * 0.06
                    sprite.blur_radius = max(sprite.blur_radius, 0.2)

        if self.interacted: return
        self.game_objects.camera_manager.zoom(rate = self.rate, scale = self.scale, center = self.center)
        self.interacted = True#sets to false when player gos away

    def player_noncollision(self):#when player doesn't collide: for grass
        self.blur_timer = C.fps
        self.interacted = False
        if self.game_objects.shader_render.shaders.get('zoom', False):
            self.game_objects.shader_render.shaders['zoom'].method = 'zoom_out'
            self.game_objects.player.shader_state.handle_input('idle')
            for sprite in self.game_objects.all_bgs:
                if sprite.parallax[0] == 1: sprite.blur_radius = 0.2
                else: sprite.blur_radius = min(1/sprite.parallax[0], 10)#limit the blur raidus for performance

class Path_col(Interactable):
    def __init__(self, pos, game_objects, size, destination, spawn):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def player_collision(self, player):
        if self.rect[3] > self.rect[2]:#if player was trvelling horizontally, enforce running in that direction
            player.currentstate.enter_state('Run_main')#infstaed of idle, should make her move a little dependeing on the direction
            player.currentstate.walk()
        else:#vertical travelling
            player.reset_movement()
            player.currentstate.enter_state('Idle_main')#infstaed of idle, should make her move a little dependeing on the direction

        self.game_objects.load_map(self.game_objects.game.state_stack[-1],self.destination, self.spawn)
        self.kill()#so that aila only collides once

class Path_inter(Interactable):
    def __init__(self, pos, game_objects, size, destination, spawn, image, sfx):
        super().__init__(pos, game_objects, sfx)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def interact(self):
        if self.sfx: self.play_sfx()
        self.game_objects.player.reset_movement()
        self.game_objects.player.currentstate.enter_state('Idle_main')#infstaed of idle, should make her move a little dependeing on the direction
        self.game_objects.load_map(self.game_objects.game.state_stack[-1],self.destination, self.spawn)

class Shade_trigger(Interactable):#it changes the colourof shade screen to a new colour specified by self.new_colour
    def __init__(self, pos, game_objects, size, colour):
        super().__init__(pos, game_objects)
        self.new_colour = [colour.g,colour.b,colour.a]
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self):
        pass

    def player_collision(self, player):#player collision
        for layer in self.layers:
            layer.shader_state.handle_input('mix_colour')

    def player_noncollision(self):#when player doesn't collide
        for layer in self.layers:
            layer.shader_state.handle_input('idle')

    def add_shade_layers(self, layers):#called from map loader
        self.layers = layers
        for layer in layers:
            layer.new_colour = self.new_colour + [layer.colour[-1]]
            layer.bounds = self.rect

class Event_trigger(Interactable):#cutscene (state) or event/quest
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.event = kwarg.get('event', False)
        self.new_state = kwarg.get('new_state', False)#if it is an event that requires new sttae, e.g. cutscene

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        self.group_distance()

    def player_collision(self, player):
        if not self.new_state:
            if self.game_objects.world_state.events.get(self.event, False): return#if event has already been done
            self.game_objects.quests_events.initiate_event(self.event)#quest or event?

        else:#if it is an event that requires new sttae, e.g. cutscene
            if self.game_objects.world_state.cutscenes_complete.get(self.event.lower(), False): return#if the cutscene has not been shown before. Shold we kill the object instead?
            if self.event == 'Butterfly_encounter':
                if not self.game_objects.world_state.statistics['kill'].get('maggot',False): return#don't do cutscene if aggrp is not chosen

            new_game_state = getattr(states, self.event)(self.game_objects.game)
            new_game_state.enter_state()
        self.kill()#is this a pronlen in re spawn?

class Interactable_bushes(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.interacted = False

    def player_collision(self, player):#player collision
        if self.interacted: return
        self.currentstate.handle_input('Once',animation_name ='hurt', next_state = 'idle')
        self.interacted = True#sets to false when player gos away

    def take_dmg(self,projectile):#when player hits with sword
        self.currentstate.handle_input('Death')

    def reset_timer(self):
        super().reset_timer()
        self.currentstate.handle_input('Idle')

    def player_noncollision(self):#when player doesn't collide
        self.interacted = False

class Cave_grass(Interactable_bushes):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/bushes/cave_grass/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

    def player_collision(self, player):
        if self.interacted: return
        self.currentstate.handle_input('Once',animation_name ='hurt', next_state = 'Idle')
        self.interacted = True#sets to false when player gos away
        self.release_particles()

    def take_dmg(self,projectile):
        super().take_dmg(projectile)
        self.release_particles(3)

    def release_particles(self, number_particles = 12):#should release particles when hurt and death
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Circle')(self.hitbox.center,self.game_objects, distance=30, lifetime=300, vel = {'wave': [3, 14]}, scale=2, fade_scale = 1.5)
            self.game_objects.cosmetics.add(obj1)

class Cocoon(Interactable):#larv cocoon in light forest
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/cocoon/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.health = 3
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def take_dmg(self,projectile):
        if self.invincibile: return
        #projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.timer_jobs['invincibility'].activate()

        if self.health > 0:
            self.currentstate.handle_input('Once', animation_name = 'hurt', next_state = 'Idle')
            #self.shader_state.handle_input('Hurt')#turn white
        else:#death
            self.invincibile = True
            self.currentstate.handle_input('Once', animation_name = 'interact', next_state = 'Interacted')
            self.game_objects.enemies.add(Maggot(self.rect.center,self.game_objects))

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Cocoon_boss(Cocoon):#boss cocoon in light forest
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/cocoon_boss/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.aggro_distance = [200,50]
        self.currentstate = states_cocoon_boss.Idle(self)
        self.item = Tungsten

    def particle_release(self):
        for i in range(0,30):
            obj1 = getattr(particles, 'Circle')(self.rect.center,self.game_objects,distance=0,lifetime=55,vel={'linear':[7,14]},dir='isotropic',scale=0.5,colour = [255,255,255,255])
            self.game_objects.cosmetics.add(obj1)

    def take_dmg(self,projectile):
        if self.invincibile: return
        self.invincibile = True
        self.game_objects.quests_events.initiate_quest('butterfly_encounter')

class Runestones(Interactable):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/runestones/' + ID_key + '/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.true_pos = self.rect.topleft
        self.hitbox.midbottom = self.rect.midbottom
        if state:
            self.currentstate = states_basic.Interacted(self)

    def interact(self):
        if type(self.currentstate).__name__ == 'Interacted': return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.currentstate.handle_input('Transform')#goes to interacted after transform
        self.game_objects.world_state.state[self.game_objects.map.level_name]['runestone'][self.ID_key] = True#write in the state dict that this has been picked up

    def reset_timer(self):#when animation finished
        super().reset_timer()
        self.game_objects.player.currentstate.handle_input('Pray_post')

class Uber_runestone(Interactable):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/uber_runestone/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.runestone_number = 0#a counter of number of activated runestrones
        self.count_runestones()

    def count_runestones(self):#append all runestone ID that have been activated.
        for level in self.game_objects.world_state.state.keys():
            for runestoneID in self.game_objects.world_state.state[level]['runestone'].keys():
                if self.game_objects.world_state.state[level]['runestone'][runestoneID] != 'idle':
                    pos = [self.rect.x+int(runestoneID)*16,self.rect.y]
                    self.game_objects.cosmetics.add(Rune_symbol(pos,runestoneID))
                    self.runestone_number += 1

    def interact(self):#when player press T
        if self.runestone_number == 25:
            pass#do a cutscene?

class Chest(Interactable):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/Chest/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health=3
        self.inventory = {'Amber_Droplet':3}
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}
        self.hitbox.midbottom = self.rect.midbottom

        if state:
            self.currentstate = states_basic.Interacted(self)

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def loots(self):#this is called when the opening animation is finished
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop, self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def take_dmg(self,projectile):
        if self.invincibile: return
        projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.timer_jobs['invincibility'].activate()

        if self.health > 0:
            self.currentstate.handle_input('Hurt')
        else:
            self.currentstate.handle_input('Opening')
            self.game_objects.world_state.state[self.game_objects.map.level_name]['chest'][self.ID_key] = True#write in the state dict that this has been picked up

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Door(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=read_files.load_sprites_dict('Sprites/animations/Door/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

class Savepoint(Interactable):#save point
    def __init__(self, pos, game_objects, map):
        super().__init__(pos, game_objects)
        self.sprites=read_files.load_sprites_dict('Sprites/animations/savepoint/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        if type(self.currentstate).__name__ == 'Outline':#single click
            self.game_objects.player.currentstate.enter_state('Pray_pre')
            self.game_objects.player.spawn_point['map'] = self.map
            self.game_objects.player.spawn_point['point'] = self.init_cord
            self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
            self.game_objects.cosmetics.add(Logo_loading(self.game_objects))
        else:#odoulbe click
            self.game_objects.player.currentstate.handle_input('special')
            new_state = states.Facilities(self.game_objects.game,'Spirit_upgrade_menu')
            new_state.enter_state()

    def reset_timer(self):#when animation finished
        super().reset_timer()
        self.game_objects.player.currentstate.handle_input('Pray_post')

class Inorinoki(Interactable):#the place where you trade soul essence for spirit or heart contrainer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/inorinoki/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def interact(self):#when player press t/y
        new_state = states.Facilities(self.game_objects.game, 'Soul_essence')
        new_state.enter_state()

class Fast_travel(Interactable):
    cost = 50
    def __init__(self,pos,game_objects,map):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/fast_travel/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

        try:#if it has been unlocked
            self.game_objects.world_state.travel_points[map]
            self.locked = False
        except:
            self.locked = True#starts locked. After paying some ambers, it unlocks and fast travel is open

    def unlock(self):#called from Fast_travel_unlock
        if self.game_objects.player.inventory['Amber_Droplet'] > self.cost:
            self.game_objects.player.inventory['Amber_Droplet'] -= self.cost
            self.locked = False
            Fast_travel.cost *= 5#increase by 5 for every unlock
            self.game_objects.world_state.save_travelpoint(self.map,self.init_cord)#self.game_objects.player.abs_dist)
            return True
        else:
            return False

    def interact(self):#when player press t/y
        if self.locked:
            type = 'Fast_travel_unlock'
            new_state = states.Facilities(self.game_objects.game,type,self)
        else:
            type = 'Fast_travel_menu'
            self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
            new_state = states.Facilities(self.game_objects.game,type)
        new_state.enter_state()

class Rhoutta_altar(Interactable):#altar to trigger the cutscane at the beginning
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/rhoutta_altar/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
        new_game_state = states.Cutscenes(self.game_objects.game,'Rhoutta_encounter')
        new_game_state.enter_state()

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Sign(Interactable):
    def __init__(self,pos,game_objects,directions):
        super().__init__(pos,game_objects)
        self.directions = directions
        self.sprites = read_files.load_sprites_dict('Sprites/animations/sign/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.symbols = Sign_symbols(self)

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Outline')

    def player_noncollision(self):#when player doesn't collide
        self.symbols.finish()
        self.currentstate.handle_input('Idle')

    def interact(self):#when player press t/y
        if self.symbols in self.game_objects.cosmetics:
            self.symbols.finish()
        else:
            self.symbols.init()
            self.game_objects.cosmetics.add(self.symbols)

class Light_crystal(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/light_crystals/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def take_dmg(self,projectile):
        if self.invincibile: return
        projectile.clash_particles(self.hitbox.center)
        self.timer_jobs['invincibility'].activate()
        self.currentstate.handle_input('Transform')
        self.game_objects.lights.add_light(self)#should be when interacted state is initialised and not on taking dmg

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Fireplace(Interactable):
    def __init__(self, pos, game_objects, on = False):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/fireplace/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom
        self.currentstate = states_fireplace.Idle(self)
        self.light_sources = []#save light references to turn be able to removr them
        if on:
            self.interact()

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Interact')#goes to interacted after transform

    def make_light(self):
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [255/255,175/255,100/255,255/255],flicker=True,radius = 100))
        self.light_sources.append(self.game_objects.lights.add_light(self, radius = 50))
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [255/255,175/255,100/255,255/255],radius = 100))

class Spikes(Interactable):#traps
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/traps/spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.rect[2],16)
        self.dmg = 1

class Spirit_spikes(Interactable):#traps
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = read_files.load_sprites_dict('Sprites/animations/traps/spirit_spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.rect[2],16)
        self.size = [32,32]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Death')

class Lightning_spikes(Interactable):#traps
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = read_files.load_sprites_dict('Sprites/animations/traps/lightning_spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 26, 16)
        self.size = [64,64]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Once')

class Grind(Interactable):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/traps/grind/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_grind.Active(self)#

        self.frequency = int(kwarg.get('frequency', -1))#infinte -> idle - active
        direction = kwarg.get('direction', '0,0')#standing still
        string_list = direction.split(',')
        self.direction = [int(num) for num in string_list]
        self.distance = int(kwarg.get('distance', 1))#standing still
        self.speed = float(kwarg.get('speed', 1))

        self.velocity = [0, 0]
        self.time = 0
        self.original_pos = pos

    def update_vel(self):
        self.velocity[0] = self.direction[0] * self.distance * math.cos(self.speed * self.time)
        self.velocity[1] = self.direction[1] * self.distance * math.sin(self.speed * self.time)

    def update(self):
        super().update()
        self.time += self.game_objects.game.dt
        self.currentstate.update()
        self.update_vel()
        self.update_pos()

    def update_pos(self):
        self.true_pos = [self.original_pos[0] + self.velocity[0]*self.game_objects.game.dt,self.original_pos[1] + self.velocity[1]*self.game_objects.game.dt]
        self.rect.topleft = self.true_pos
        self.hitbox.center = self.rect.center

    def group_distance(self):
        pass

    def player_collision(self, player):#player collision
        player.take_dmg(1)

    def take_dmg(self, projectile):#when player hits with e.g. sword
        if hasattr(projectile, 'sword_jump'):#if it has the attribute
            projectile.sword_jump()

class Lever(Interactable):
    def __init__(self, pos, game_objects, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/lever/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.ID_key = ID_key#an ID to match with the gate and an unique ID key to identify which item that the player is intracting within the world
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

        if self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'].get(self.ID_key, False):
            self.currentstate = states_lever.Down(self)
        else:
            self.currentstate = states_lever.Idle(self)
            self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key] = False

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def take_dmg(self,projectile):
        if self.invincibile: return
        self.timer_jobs['invincibility'].activate()
        projectile.clash_particles(self.hitbox.center)

        self.currentstate.handle_input('Transform')
        self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key] = not self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key]#write in the state dict that this has been picked up
        self.gate.currentstate.handle_input('Transform')

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def add_gate(self, gate):#called from map loader
        self.gate = gate
        if type(self.currentstate).__name__ == 'Down':
            self.gate.currentstate.enter_state('Down')
        else:
            self.gate.currentstate.enter_state('Erect')

#timer toools: activate with the attrubute activate, which will run until the specified duration is run out
class Timer():
    def __init__(self, entity, duration):
        self.entity = entity
        self.duration = duration

    def activate(self):#add timer to the entity timer list
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)

    def update(self):
        self.lifetime -= self.entity.game_objects.game.dt * self.entity.game_objects.player.slow_motion
        if self.lifetime < 0:
            self.deactivate()

class General_Timer(Timer):#when lifetime is 0, it calls the timeout of entety
    def __init__(self, entity, duration, function):
        super().__init__(entity, duration)
        self.lifetime = duration
        self.function = function

    def deactivate(self):
        self.function()

class Invincibility_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.entity.invincibile = False#a flag to check if one should take damage

    def activate(self):#called when taking a dmg
        super().activate()
        self.entity.invincibile = True

    def deactivate(self):
        super().deactivate()
        self.entity.invincibile = False

class Wet_timer(Timer):#"a wet status". activates when player baths, and spawns particles that drops from player
    def __init__(self,entity, duration):
        super().__init__(entity, duration)
        self.game_objects = entity.game_objects#need for general timer
        self.spawn_frequency = 5#how often to spawn particle
        self.spawn_timer = General_Timer(self, self.spawn_frequency, self.time_out)

    def activate(self, water_tint):#called when aila bathes (2D water)
        self.lifetime = self.duration#reset the duration
        self.water_tint = water_tint
        self.drop()
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.entity.timers.append(self)

    def update(self):
        super().update()
        self.spawn_timer.update()

    def time_out(self):#called when geenral timer runs out
        self.spawn_timer.lifetime = self.spawn_frequency#reset the time
        self.drop()

    def drop(self):
        pos = [self.entity.hitbox.centerx + random.randint(-5,5), self.entity.hitbox.centery + random.randint(-5,5)]
        obj1 = particles.Circle(pos, self.game_objects, lifetime = 50, dir = [0, -1], colour = [self.water_tint[0]*255, self.water_tint[1]*255, self.water_tint[2]*255, 255], vel = {'gravity': [0, -1]}, gravity_scale = 0.2, fade_scale = 2, gradient=0)
        self.game_objects.cosmetics.add(obj1)

class Sword_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def activate(self):#called when sword is swang
        super().activate()
        self.entity.flags['sword_swinging'] = True

    def deactivate(self):
        super().deactivate()
        self.entity.flags['sword_swinging'] = False

class Jump_buffer_timer(Timer):#can be combined with shroomjump?
    def __init__(self, entity, duration):
        super().__init__(entity, duration)#called from player states, when pressing jump

    def update(self):#called everyframe after activation (activated after pressing jump)
        if self.entity.flags['ground']:#start jumping if we a re on the ground
            self.entity.flags['ground'] = False
            self.entity.velocity[1] = C.jump_vel_player#start jumping on this frame
            self.entity.currentstate.handle_input('jump')#handle if we should go to jump state
            self.entity.timer_jobs['air'].activate()
            self.deactivate()
        super().update()#need to be after

class Dash_buffer_timer(Timer):#ground dash buffer time
    def __init__(self, entity, duration):
        super().__init__(entity, duration)#called from player states, when pressing dash

    def update(self):#called everyframe after activation (activated after pressing jump)
        if self.entity.flags['ground']:#start dashing if we a re on the ground
            self.entity.flags['ground'] = False
            self.entity.currentstate.handle_input('dash')#handle if we should go to jump state
            self.deactivate()
        super().update()#need to be after

class Air_timer(Timer):#activated when jumped. It keeps a constant vertical velocity for the duration. Needs to be deactivated when releasing jump bottom
    def __init__(self, entity, duration):
        super().__init__(entity, duration)

    def update(self):#called everyframe after activation (activated after jumping)
        self.entity.velocity[1] = C.jump_vel_player
        super().update()#need to be after

class Cayote_timer(Timer):#a timer to check how long time one has not been on ground
    def __init__(self,entity, duration):
        super().__init__(entity, duration)

    def activate(self):#called when entering fall run or fall stand
        if self.entity.flags['ground']:#if we fall from a plotform
            super().activate()

    def deactivate(self):#called when timer runs out
        super().deactivate()
        self.entity.flags['ground'] = False

class Shroomjump_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.shrooming = False

    def activate(self):#called when pressed jump putton and/or landing on a shroom
        if self.shrooming:#second time entering (pressing or landing on shroom)
            self.entity.velocity[1] = -15
            return
        super().activate()
        self.shrooming = True

    def deactivate(self):#called when timer expires
        super().deactivate()
        self.shrooming = False

class Wall_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.active = False

    def activate(self):
        super().activate()
        self.active = True

    def deactivate(self):
        super().deactivate()
        self.active = False

    def handle_input(self,input):#called from handle press input in player states
        #return
        if not self.active: return
        if input=='a':#pressed jump
            #self.entity.velocity[0] = -self.entity.dir[0]*10
            self.entity.velocity[1] = -7#to get a vertical velocity

class Wall_timer_2(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def activate(self,dir):#add timer to the entity timer list
        super().activate()
        self.dir = dir.copy()

    def update(self):
        self.check_sign()
        super().update()

    def check_sign(self):
        if self.entity.dir[0]*self.dir[0]>=0:#if it is zero or same direction
            self.entity.dir[0] = 0
        else:#if aila change direction
            self.entity.dir[0] = -self.dir[0]
            if self not in self.entity.timers: return#do not remove if the timer is not inside
            self.entity.timers.remove(self)

    def deactivate(self):#lifetime
        super().deactivate()
        self.entity.dir[0] = self.dir[0]
