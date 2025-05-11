import pygame, random, sys, math
import read_files, particles, animation, dialogue, groups, backpack, modifier_damage, modifier_movement, seeds
import constants as C

from entities_base import Enemy, Flying_enemy, NPC, Boss, Projectiles, Melee, Loot, Enemy_drop, Interactable, Interactable_item
from entities_core import Staticentity, Animatedentity, Platform_entity, Character

#from folders
from ai import reindeer_ai, AI_mygga_crystal, AI_crab_crystal, AI_froggy, AI_butterfly, AI_maggot, AI_wall_slime, AI_vatt, AI_kusa, AI_enemy_flying, AI_bird, AI_enemy, AI_mygga, AI_larv
from states import hitstop_states, states_savepoint, states_mygga_crystal, states_crab_crystal, states_exploding_mygga, states_droplets, states_twoD_liquid, states_death, states_lever, states_grind, states_portal, states_froggy, states_sword, states_fireplace, states_shader_guide, states_butterfly, states_cocoon_boss, states_maggot, states_horn_vines, states_camerastop, states_player, states_traps, states_NPC, states_enemy, states_vatt, states_enemy_flying, reindeer_states, states_bird, states_kusa, states_rogue_cultist, states_sandrew, states_blur, states_shader, states_basic

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

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
        if self.layers:  # Release layer if it exists, used for thre blurring
            self.layers.release()

class BG_Fade(BG_Block):
    def __init__(self, pos, game_objects, img, parallax, positions, ID):
        super().__init__(pos, game_objects, img, parallax)
        self.shader_state = states_shader.Idle(self)
        self.make_hitbox(positions, pos)
        self.interacted = False
        self.sounds = read_files.load_sounds_list('audio/SFX/bg_fade/')
        self.children = []#will append overlapping bg_fade to make "one unit"
        self.id = str(ID)

        if self.game_objects.world_state.state[self.game_objects.map.level_name]['bg_fade'].get(self.id, False):#if it has been interacted with already
            self.interact()

    def make_hitbox(self, positions, offset_position):#the rect is the whole screen, need to make it correctly cover the surface part, some how
        x, y = [],[]
        for pos in positions:
            x.append(pos[0]+offset_position[0])
            y.append(pos[1]+offset_position[1])
        width = max(x) - min(x)
        height = max(y) - min(y)
        self.hitbox = pygame.Rect(min(x),min(y),width,height)

    def update(self):
        self.shader_state.update()

    def interact(self):
        self.shader_state.handle_input('alpha')
        self.interacted = True
        self.game_objects.world_state.state[self.game_objects.map.level_name]['bg_fade'][self.id] = True

    def add_child(self, child):
        self.children.append(child)
        if self.interacted: child.interact()

    def draw(self, target):#called before draw in group
        self.shader_state.draw()
        super().draw(target)

    def player_collision(self, player):
        if self.interacted: return
        self.game_objects.sound.play_sfx(self.sounds[0])
        self.interact()
        for child in self.children:
            child.interact()

#shaders -> should this be here or in enteties_parallx or elsewhere?
class Portal_2(Staticentity):#same as portal but masked based. Doesnt work becasue the mask is repeated for some reason
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.currentstate = states_portal.Spawn(self)

        self.empty_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
        self.noise_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.mask_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)

        self.bg_distort_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#bg
        self.bg_grey_layer = game_objects.game.display.make_layer(self.game_objects.game.window_size)#entetirs

        self.rect = pygame.Rect(pos[0], pos[1], self.empty_layer.texture.width, self.empty_layer.texture.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.centerx, self.rect.centery, 32, 32)
        self.time = 0

        self.radius = 0
        self.thickness = 0
        self.thickness_limit = 0.1
        self.radius_limit = 0.4#one is screen size

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
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #mask
        self.game_objects.shaders['circle_pos']['radius'] = self.radius
        self.game_objects.shaders['circle_pos']['color'] = [255,255,255,255]
        self.game_objects.shaders['circle_pos']['gradient'] = 1
        self.game_objects.game.display.render(self.empty_layer.texture, self.mask_layer, shader = self.game_objects.shaders['circle_pos'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort_2']['TIME'] = self.time
        self.game_objects.shaders['distort_2']['maskTexture'] = self.mask_layer.texture
        self.game_objects.shaders['distort_2']['center'] = blit_pos
        self.game_objects.shaders['distort_2']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort_2']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort_2'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['distort_2'])#make them gre

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
        self.thickness_limit = 0.1
        self.radius_limit = 1#one is screen size

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
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [50,50]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #portal
        self.game_objects.shaders['portal']['TIME'] = self.time*0.1
        self.game_objects.shaders['portal']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['portal']['radius'] = self.radius
        self.game_objects.shaders['portal']['thickness'] = self.thickness
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.bg_distort_layer, position = blit_pos, shader = self.game_objects.shaders['portal'])

        #noise with scroll
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty_layer.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #distortion on bg
        self.game_objects.shaders['distort']['TIME'] = self.time
        self.game_objects.shaders['distort']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['distort']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['distort']['center'] = [self.rect.center[0] - self.game_objects.camera_manager.camera.scroll[0], self.rect.center[1] - self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['distort']['radius'] = self.radius
        self.game_objects.shaders['distort']['tint'] = [1,1,1]
        self.game_objects.game.display.render(self.bg_distort_layer.texture, self.game_objects.game.screen, shader=self.game_objects.shaders['distort'])#make a copy of the screen

        #distortion on enteties
        self.game_objects.shaders['distort']['tint'] = [0.39, 0.78, 1]
        self.game_objects.game.display.render(self.bg_grey_layer.texture, self.empty_layer, shader = self.game_objects.shaders['distort'])#make them grey
        self.game_objects.shaders['edge_light']['TIME'] = self.time
        self.game_objects.shaders['edge_light']['textureNoise'] = self.noise_layer.texture
        self.game_objects.game.display.render(self.empty_layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['edge_light'])#make them grey

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
        self.time += self.game_objects.game.dt

    def draw(self, target):
        #noise
        #self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        #self.game_objects.shaders['noise_perlin']['u_time'] =self.time * 0.01
        #self.game_objects.shaders['noise_perlin']['scroll'] =[0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        #self.game_objects.shaders['noise_perlin']['scale'] = [2,2]#"standard"
        #self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #self.game_objects.shaders['cloud']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['cloud']['time'] = self.time
        self.game_objects.shaders['cloud']['camera_scroll'] = [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        #self.game_objects.shaders['cloud']['texture_size'] = self.size

        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['cloud'])

class Waterfall(Staticentity):
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos, game_objects)
        self.parallax = parallax

        self.size = size
        self.empty = game_objects.game.display.make_layer(size)
        self.screen_copy = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        self.blur_layer = game_objects.game.display.make_layer(size)
        self.time = 5#offset the time

        sounds = read_files.load_sounds_dict('audio/SFX/environment/waterfall/')
        self.channel = self.game_objects.sound.play_sfx(sounds['idle'][0], loop = -1)

    def release_texture(self):
        self.empty.release()
        self.noise_layer.release()
        self.screen_copy.release()
        self.blur_layer.release()
        self.channel.fadeout(300)

    def set_volume(self):
        width = self.game_objects.game.window_size[0]
        height = self.game_objects.game.window_size[1]
        center_blit_pos = [self.true_pos[0] + self.size[0]*0.5-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.true_pos[1]+ self.size[1]*0.5-self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        distance_to_screencenter = ((center_blit_pos[0] - width * 0.5)**2 + (center_blit_pos[1]-height * 0.5) ** 2)**0.5
        max_distance = ((width*0.5)**2 + (height*0.5)**2)**0.5
        normalized_distance = max(0, min(1, 1 - (distance_to_screencenter / max_distance)))#clamp it to 0, 1
        self.channel.set_volume(0.5 * normalized_distance)

    def update(self):
        self.time += self.game_objects.game.dt * 0.01
        self.set_volume()

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
        self.game_objects.shaders['waterfall']['SCREEN_TEXTURE'] = self.screen_copy.texture
        self.game_objects.shaders['waterfall']['TIME'] = self.time

        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['waterfall']['section'] = [blit_pos[0],blit_pos[1],self.size[0],self.size[1]]

        if self.parallax[0] == 1:#TODO, blue state #don't blur if there is no parallax
            self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['waterfall'])
        else:
            self.blur_layer.clear(0, 0, 0, 0)
            self.game_objects.shaders['blur']['blurRadius'] = 1/self.parallax[0]#set the blur redius
            self.game_objects.game.display.render(self.empty.texture, self.blur_layer, shader = self.game_objects.shaders['waterfall'])
            self.game_objects.game.display.render(self.blur_layer.texture, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['blur'])

class Reflection(Staticentity):#water, e.g. village
    def __init__(self, pos, game_objects, parallax, size, **kwarg):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.offset = int(kwarg.get('offset', 10))
        self.squeeze = 1
        self.reflect_rect = pygame.Rect(self.rect.left, self.rect.top, size[0], size[1]/self.squeeze)

        self.empty = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.water_noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(game_objects.game.window_size)
        #self.game_objects.shaders['water']['u_resolution'] = game_objects.game.window_size
        self.texture_parallax = int(kwarg.get('texture_parallax', 1))#0 means no parallax on the texture
        self.water_texture_on = kwarg.get('water_texture_on', True)

        self.time = 0
        self.water_speed = kwarg.get('speed', 0)
        self.blur_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.colour = (0.39, 0.78, 1, 1)

        sounds = read_files.load_sounds_dict('audio/SFX/environment/river/')
        self.channel = self.game_objects.sound.play_sfx(sounds['idle'][0], loop = -1, vol = 0.2)

    def release_texture(self):#called when .kill() and empty group
        self.empty.release()
        self.noise_layer.release()
        self.water_noise_layer.release()
        self.blur_layer.release()
        self.screen_copy.release()
        self.channel.fadeout(300)

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

        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.screen_copy)#stuff to reflect

        #water
        self.game_objects.shaders['water_perspective']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['water_perspective']['noise_texture2'] = self.water_noise_layer.texture
        self.game_objects.shaders['water_perspective']['TIME'] = self.time
        self.game_objects.shaders['water_perspective']['SCREEN_TEXTURE'] = self.screen_copy.texture#stuff to reflect
        self.game_objects.shaders['water_perspective']['water_speed'] = self.water_speed
        self.game_objects.shaders['water_perspective']['water_albedo'] = self.colour
        self.game_objects.shaders['water_perspective']['texture_parallax'] = self.texture_parallax
        self.game_objects.shaders['water_perspective']['water_texture_on'] = self.water_texture_on


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

class TwoD_liquid(Staticentity):#inside interactables_fg group. fg because in front of player
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
        player.movement_manager.add_modifier('TwoD_liquid')
        vel_scale = player.velocity[1] / C.max_vel[1]
        self.splash(player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [7 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        player.timer_jobs['wet'].deactivate()#stop dropping if inside the water again
        self.interacted = True
        self.currentstate.player_collision(player)

    def player_noncollision(self):
        if not self.interacted: return
        self.game_objects.player.movement_manager.remove_modifier('TwoD_liquid')
        self.game_objects.player.timer_jobs['wet'].activate(self.currentstate.liquid_tint)#water when player leaves
        vel_scale = abs(self.game_objects.player.velocity[1] / C.max_vel[1])
        self.splash(self.game_objects.player.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [10 * vel_scale, 14 * vel_scale]}, fade_scale = 0.3, gradient=0)
        self.interacted = False
        self.currentstate.player_noncollision()

    def splash(self,  pos, number_particles=20, **kwarg):#called from states, upoin collusions
        for i in range(0, number_particles):
            obj1 = particles.Circle(pos, self.game_objects, **kwarg)
            self.game_objects.cosmetics.add(obj1)

    def seed_collision(self, seed):
        vel_scale = [abs(seed.velocity[0])/20,abs(seed.velocity[1])/ 20]
        self.splash(seed.hitbox.midbottom, lifetime = 100, dir = [0,1], colour = [self.currentstate.liquid_tint[0]*255, self.currentstate.liquid_tint[1]*255, self.currentstate.liquid_tint[2]*255, 255], vel = {'gravity': [14 * vel_scale[0], 7 * vel_scale[0]]}, fade_scale = 0.3, gradient=0, scale = 2)
        seed.seed_spawner.spawn_bubble()

class Up_stream(Staticentity):#a draft that can lift enteties along a direction
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.hitbox = pygame.Rect(pos[0] + size[0]* 0.2 * 0.5, pos[1], size[0] * 0.8, size[1])#adjust the hitbox size based on texture
        self.time = 0

        horizontal = kwarg.get('horizontal', 0)
        vertical = kwarg.get('vertical', 0)
        normalise = (horizontal**2 + vertical**2)**0.5
        self.dir = [horizontal/normalise, vertical/normalise]

        sounds = read_files.load_sounds_dict('audio/SFX/environment/up_stream/')
        self.channel = game_objects.sound.play_sfx(sounds['idle'][0], loop = -1, vol = 0.5)

    def release_texture(self):
        self.image.release()
        self.channel.fadeout(300)

    def update(self):
        self.time += self.game_objects.game.dt

    def draw(self, target):
        self.game_objects.shaders['up_stream']['dir'] = self.dir
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['up_stream'])#shader render

    def player_collision(self, player):#player collision
        player.velocity[0] += self.dir[0] * self.game_objects.game.dt
        context = player.movement_manager.resolve()
        player.velocity[1] += self.dir[1] * self.game_objects.game.dt * 0.5 * context.upstream + self.dir[1] * int(player.collision_types['bottom'])#a small inital boost if on ground

    def player_noncollision(self):
        pass

class Smoke(Staticentity):#2D smoke
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
        self.noise_layer.release()

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

class Rainbow(Staticentity):
    def __init__(self, pos, game_objects, size, parallax, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.parallax = parallax

    def release_texture(self):
        self.image.release()

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['rainbow'])#shader render

class Death_fog(Staticentity):#2D explosion
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.size = size
        self.time = 0

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

    def update(self):
        self.time += self.game_objects.game.dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['death_fog']['TIME'] = self.time*0.01
        self.game_objects.shaders['death_fog']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['death_fog']['velocity'] = [0, 0]
        self.game_objects.shaders['death_fog']['fog_color'] = [0, 0, 0, 1]

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['death_fog'])#shader render

class Arrow_UI(Staticentity):#for thuder charge state
    def __init__(self, pos, game_objects, dir = [0, -1]):
        super().__init__(pos, game_objects)
        self.image = Arrow_UI.image
        self.time = 0
        self.dir = dir#default direction

    def release_texture(self):
        pass

    def update(self):
        self.time += self.game_objects.game.dt

    def pool(game_objects):
        size = (200,100)#to make the arrow more uniform when roated
        Arrow_UI.image = game_objects.game.display.make_layer(size)

    def draw(self, target):
        self.game_objects.shaders['arrow']['TIME'] = self.time*0.01
        self.game_objects.shaders['arrow']['moonDirection'] = self.dir

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['arrow'])#shader render

class Thunder_ball(Staticentity):#not used
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.time = 0

    def update(self):
        self.time += self.entity.game_objects.game.dt*0.01

    def draw(self, target):
        self.entity.game_objects.shaders['thunder_ball']['iTime'] = self.time
        self.entity.game_objects.shaders['thunder_ball']['iResolution'] = self.size

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['thunder_ball'])#shader render

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

class Player(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/aila/')
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/aila/texture/', game_objects)
        self.normal_maps = read_files.load_sprites_dict('Sprites/enteties/aila/normal/', game_objects)
        self.image = self.sprites['idle_main'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes

        self.max_health = 15
        self.max_spirit = 4
        self.health = 14
        self.spirit = 2

        self.projectiles = game_objects.fprojectiles
        self.sword = Aila_sword(self)
        self.abilities = Player_abilities(self)#spirit (thunder,migawari etc) and movement /dash, double jump and wall glide)

        self.states = {'Idle':True, 'Walk':True, 'Run':True,'Pray':True,'Stand_up':True,
                     'Jump':True,'Fall':True,'Death':True,
                     'Invisible':True,'Hurt':True,'Spawn':True,'Plant_bone':True,
                     'Sword_run1':True,'Sword_run2':True,'Sword_stand1':True,'Sword_stand2':True,
                     'Air_sword2':True,'Air_sword1':True,'Sword_up':True,'Sword_down':True,
                     'Dash_attack':True,'Ground_dash':True,'Air_dash':True,'Belt_glide':True, 'Wall_glide':True,'Double_jump':False,
                     'Thunder':True,'Shield':True, 'Slow_motion':True,
                     'Bow':True,'Counter':True, 'Sword_fall':True,'Sword_jump1':True, 'Sword_jump2':True, 'Dash_jump':True, 'Wind':True,
                     'Heal': True}

        self.flags = {'ground': True, 'invincibility': False, 'shroompoline': False, 'attack_able': True}# flags to check if on ground (used for jumpåing), #a flag to make sure you can only swing sword when this is False
        self.currentstate = states_player.Idle_main(self)
        self.death_state = states_death.Idle(self)#this one can call "normal die" or specifal death (for example cultist encounter)

        self.backpack = backpack.Backpack(self)

        self.timers = []#a list where timers are append whe applicable, e.g. wet status
        self.timer_jobs = {'wet': Wet_status(self, 60)}#these timers are activated when promt and a job is appeneded to self.timer.
        self.reset_movement()

        self.damage_manager = modifier_damage.Damage_manager(self)
        self.movement_manager = modifier_movement.Movement_manager()

        self.colliding_platform = None#save the last collising platform
        #self.shader_state = states_shader.Thunder_ball(self)

    def ramp_down_collision(self, ramp):#when colliding with platform beneth
        super().ramp_down_collision(ramp)
        self.colliding_platform = ramp#save the latest platform

    def down_collision(self, block):#when colliding with platform beneth
        super().down_collision(block)
        self.colliding_platform = block#save the latest platform

    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block, type)
        self.colliding_platform = block#save the latest platform

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block, type)
        self.colliding_platform = block#save the latest platform

    def update_vel(self):#called from hitsop_states
        context = self.movement_manager.resolve()
        self.velocity[1] += self.slow_motion*self.game_objects.game.dt*(self.acceleration[1]-self.velocity[1]*context.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        self.velocity[0] += self.slow_motion*self.game_objects.game.dt*(self.dir[0]*self.acceleration[0] - context.friction[0]*self.velocity[0])

    def take_dmg(self, dmg = 1):#called from collisions
        return self.damage_manager.take_damage(dmg)

    def apply_damage(self, dmg):#called from damage_manager
        self.flags['invincibility'] = True
        self.health -= dmg# * self.dmg_scale#a omamori can set the dmg_scale to 0.5
        self.game_objects.UI.hud.remove_hearts(dmg)# * self.dmg_scale)#update UI

        if self.health > 0:#check if dead¨
            self.game_objects.timer_manager.start_timer(C.invincibility_time_player, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            self.shader_state.handle_input('Hurt')#turn white and shake
            self.shader_state.handle_input('Invincibile')#blink a bit
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state or interupt attacks?
            self.emit_particles(lifetime = 40, scale=3, colour=[0,0,0,255], fade_scale = 7,  number_particles = 60 )
            self.game_objects.cosmetics.add(Slash(self.hitbox.center,self.game_objects))#make a slash animation

            self.game_objects.time_manager.modify_time(time_scale = 0, duration = 20)
            self.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 20, scale = 0.9)

            self.game_objects.shader_render.append_shader('chromatic_aberration', duration = 20)
        else:#if health < 0
            self.game_objects.signals.emit('player_died')#emit a signal that player died
            self.death_state.die()#depending on gameplay state, different death stuff should happen

    def die(self):#called from idle death_state, also called from vertical acid
        self.animation.update()#make sure you get the new animation
        self.game_objects.cosmetics.add(Blood(self.hitbox.center, self.game_objects, dir = self.dir))#pause first, then slow motion
        self.game_objects.time_manager.modify_time(time_scale = 0.4, duration = 100)#sow motion
        self.game_objects.time_manager.modify_time(time_scale = 0, duration = 50)#freeze

    def dead(self):#called when death animation is finished
        self.game_objects.world_state.update_statistcis('death')#count the number of times aila has died
        self.game_objects.game.state_manager.enter_state(state_name = 'Death', category = 'game_states_cutscenes')

    def heal(self, health = 1):
        self.health += health
        self.game_objects.UI.hud.update_hearts()#update UI

    def consume_spirit(self, spirit = 1):
        self.spirit -= spirit
        self.game_objects.UI.hud.remove_spirits(spirit)#update UI

    def add_spirit(self, spirit = 1):
        self.spirit += spirit
        self.game_objects.UI.hud.update_spirits()#update UI

    def reset_movement(self):#called when loading new map or entering conversations
        self.acceleration =  [0, C.acceleration[1]]
        self.friction = C.friction_player.copy()
        self.time = 0

    def update(self):
        self.movement_manager.update()#update the movement manager
        self.hitstop_states.update()
        self.backpack.necklace.update()
        self.update_timers()

    def draw(self, target):#called in group
        self.shader_state.draw()
        self.blit_pos = (round(self.true_pos[0]-self.game_objects.camera_manager.camera.true_scroll[0]), round(self.true_pos[1]-self.game_objects.camera_manager.camera.true_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

        #normal map draw
        self.game_objects.shaders['normal_map']['direction'] = -self.dir[0]#the normal map shader can invert the normal map depending on direction
        self.game_objects.game.display.render(self.normal_maps[self.animation.animation_name][self.animation.image_frame], self.game_objects.lights.normal_map, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.game_objects.shaders['normal_map'])#should be rendered on the same position, image_state and frame as the texture

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def on_cayote_timeout(self):
        self.flags['ground'] = False
        self.colliding_platform = None

    def on_shroomjump_timout(self):
        self.flags['shroompoline'] = False

class Flower_butterfly(Flying_enemy):#peaceful ones
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/flower_butterfly/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/flower_butterfly/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 1
        self.aggro_distance = [0,0]
        self.game_objects.lights.add_light(self, colour = [77/255,168/255,177/255,200/255], interact = False)
        self.flags['aggro'] = False

    def update(self):
        super().update()
        obj1 = particles.Floaty_particles(self.rect.center, self.game_objects, distance = 0, vel = {'linear':[0.1,-1]}, dir = 'isotropic')
        self.game_objects.cosmetics2.add(obj1)

class Mygga(Flying_enemy):#a non aggro mygga that roams around
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.aggro_distance = [0, 0]

class Mygga_chase(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
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
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
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

class Mygga_suicide(Flying_enemy):#torpedo and explode
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
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
    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def down_collision(self, block):
        super().down_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def top_collision(self, block):
        super().top_collision(block)
        self.currentstate.handle_input('collision')#for suicide

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        super().ramp_down_collision(ramp)
        self.currentstate.handle_input('collision')#for suicide

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        super().ramp_top_collision(ramp)
        self.currentstate.handle_input('collision')#for suicide

class Mygga_colliding(Flying_enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.velocity = [random.randint(-3,3),random.randint(-3,3)]
        self.dir[0] = sign(self.velocity[0])
        self.AI.enter_AI('idle')

    def walk(self, time):#called from walk state
        pass

    def update_vel(self):
        pass

    #ramp collisions
    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.top = ramp.target
        self.collision_types['top'] = True
        self.velocity[1] *= -1

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.bottom = ramp.target
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1

    #platform collision
    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = -1

    def left_collision(self, block, type = 'Wall'):
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

class Mygga_roaming_projectile(Mygga_colliding):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.AI.enter_AI('roaming_attack', frequency = 150)

    def attack(self):#called from roaming AI
        dirs = [[1,1],[-1,1],[1,-1],[-1,-1]]
        for direction in dirs:
            obj = Projectile_1(self.hitbox.center, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)

class Mygga_crystal(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/mygga_crystal/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3

        self.AI = AI_mygga_crystal.Patrol(self)
        self.currentstate = states_mygga_crystal.Idle(self)

        self.flee_distance = [50, 50]#starting fleeing if too close
        self.attack_distance = [100, 100]#attack distance
        self.aggro_distance = [150, 100]#start chasing

    def attack(self):#called from roaming AI
        dirs = [[1,1], [-1,1], [1,-1], [-1,-1]]
        for direction in dirs:
            obj = Poisonblobb(self.hitbox.topleft, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)

    def chase(self, direction):#called from AI: when chaising
        self.velocity[0] += direction[0]*0.5
        self.velocity[1] += direction[1]*0.5

    def patrol(self, position):#called from AI: when patroling
        self.velocity[0] += (position[0]-self.rect.centerx) * 0.002
        self.velocity[1] += (position[1]-self.rect.centery) * 0.002

class Mygga_exploding(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/mygga_exploding/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/exploding_mygga/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 4
        self.attack_distance = [20,20]
        self.aggro_distance = [150,100]
        self.currentstate = states_exploding_mygga.Idle(self)

    def killed(self):
        self.game_objects.sound.play_sfx(self.sounds['explosion'][0], vol = 0.2)
        self.projectiles.add(Hurt_box(self, size = [64,64], lifetime = 30, dir = [0,0]))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration

class Crab_crystal(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/crab_crystal/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 16, 16)

        self.currentstate = states_crab_crystal.Idle(self)
        self.AI = AI_crab_crystal.AI(self)

        self.hide_distance = [100, 50]#the distance to hide
        self.fly_distance = [150, 50]#the distance to hide
        self.attack_distance = [250, 50]
        self.aggro_distance = [300, 50]

    def chase(self, dir = 1):#called from AI: when chaising
        self.velocity[0] += dir*0.6

    def take_dmg(self,dmg):
        return self.currentstate.take_dmg(dmg)

    def attack(self):#called from currenrstate
        for i in range(0, 3):
            vel = random.randint(-3,3)
            new_projectile = Poisonblobb(self.rect.midtop, self.game_objects, dir = [1, -1], amp = [vel, 4])
            self.game_objects.eprojectiles.add(new_projectile)

class Froggy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/froggy/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health = 1
        self.flags['aggro'] = False
        self.attack_distance = [150,50]

        self.currentstate = states_froggy.Idle(self)
        self.shader_state = states_shader.Idle(self)
        self.AI = AI_froggy.AI(self)
        self.inventory = {'Amber_droplet':random.randint(5,15)}#thigs to drop wgen killed

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
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/sandrew/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [200, 25]
        self.aggro_distance = [250, 25]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack = Hurt_box

class Vildswine(Enemy):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/vildswine/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [200, 25]
        self.aggro_distance = [250, 25]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack = Hurt_box

class Rav(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/rav/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)
        self.aggro_distance = [200, 20]#at which distance to the player when you should be aggro -> negative means no
        self.attack_distance = [50, 20]
        self.health = 3
        self.chase_speed = 1

    def attack(self):#called from states, attack main
        attack = Hurt_box(self, lifetime = 10, dir = self.dir, size = [32, 32])#make the object
        self.projectiles.add(attack)#add to group but in main phase

class Vatt(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/vatt/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)

        self.health = 3
        self.spirit = 3
        self.flags['aggro'] = False

        self.currentstate = states_vatt.Idle(self)
        self.AI = AI_vatt.AI(self)
        self.attack_distance = [60, 30]

    def turn_clan(self):#this is acalled when tranformation is finished
        for enemy in self.game_objects.enemies.sprites():
            if type(enemy).__name__ == 'Vatt':
                enemy.flags['aggro'] = True
                enemy.AI.handle_input('Hurt')

    def patrol(self, direction):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3 * direction[0]

class Maggot(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/maggot/',game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/maggot/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,30)
        self.currentstate = states_maggot.Fall_stand(self)
        self.AI = AI_maggot.Idle(self)
        self.health = 1

        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.friction[0] = C.friction[0]*2

class Larv_base(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.AI = AI_larv.Idle(self)

    def walk(self):
        self.velocity[0] += self.dir[0]*0.22

    def knock_back(self, dir):
        super().knock_back(dir)
        self.AI = AI_larv.Idle(self, carry_dir = False, timer = 40)

    #pltform collisions.
    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block, type)
        if self.dir[0] > 0:
            self.AI = AI_larv.Idle(self, carry_dir = True, timer = 60)

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block, type)
        if self.dir[0] < 0:
            self.AI = AI_larv.Idle(self, carry_dir = True, timer = 60)

class Larv(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/larv/', game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/enemies/larv/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.attack_distance = [0,0]

    def loots(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery - 10]
        number = random.randint(2, 4)
        for i in range(0, number):
            obj = Larv_jr(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Larv_jr(Larv_base):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/larv_jr/',game_objects,True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],22,12)
        self.attack_distance = [0,0]
        self.init_x = self.rect.x
        self.patrol_dist = 100
        self.health = 3

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('larv_jr_killed')#emit this signal

class Larv_poison(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/larv_poison/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.aggro_distance = [180,150]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack_distance = [200,180]

    def attack(self):#called from states, attack main
        attack = Poisonblobb(self.rect.topleft, self.game_objects, dir = self.dir)#make the object
        self.projectiles.add(attack)#add to group but in main phase

class Larv_wall(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/slime_wall/', game_objects, flip_x = True)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()#pygame.Rect(pos[0],pos[1],16,16)

        self.angle = 0
        self.friction = [0.1, 0.1]
        self.clockwise = -1#1 is clockqise, -1 is counter clockwise
        self.AI = AI_wall_slime.Floor(self)
        self.dir[0] = self.clockwise

    def update_vel(self):#called from hitsop_states
        self.velocity[0] += self.slow_motion * self.game_objects.game.dt * (self.acceleration[0] - self.friction[0] * self.velocity[0])
        self.velocity[1] += self.slow_motion * self.game_objects.game.dt * (self.acceleration[1] - self.friction[1] * self.velocity[1])

    def knock_back(self,dir):
        pass

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0, shader = self.shader)#shader render

class Shroompoline(Enemy):#an enemy or interactable?
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/shroompolin/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box = pygame.Rect(pos[0],pos[1],32,10)
        self.flags['aggro'] = False#player collision
        self.flags['invincibility'] = True

    def player_collision(self, player):
        if self.game_objects.player.velocity[1] > 0:#going down
            offset = self.game_objects.player.velocity[1] + 1
            if self.game_objects.player.hitbox.bottom < self.jump_box.top + offset:
                self.currentstate.enter_state('Hurt')
                self.game_objects.player.velocity[1] = -10
                player.flags['shroompoline'] = True
                self.game_objects.player.currentstate.enter_state('Jump_main')
                self.game_objects.timer_manager.start_timer(C.shroomjump_timer_player, player.on_shroomjump_timout)#adds a timer to timer_manager and sets self.invincible to false after a while

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
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites=read_files.load_sprites_dict('Sprites/enteties/enemies/cultist_rogue/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 40, 40)
        self.health = 3
        self.attack_distance = [80,10]
        self.currentstate = states_rogue_cultist.Idle(self)

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('cultist_killed')

class Cultist_warrior(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/cultist_warrior/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 3
        self.attack_distance = [80,10]

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('cultist_killed')

class Shadow_enemy(Enemy):#enemies that can onlly take dmg in light -> dark forst
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def check_light(self):
        for light in self.game_objects.lights.lights_sources:
            if not light.shadow_interact: continue
            collision = self.hitbox.colliderect(light.hitbox)
            if collision:
                self.light()
                return
        self.no_light()

    def no_light(self):
        self.flags['invincibility'] = True

    def light(self):
        self.flags['invincibility'] = False

class Shadow_warrior(Shadow_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/enemies/cultist_warrior/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 3
        self.attack_distance = [80,10]

    def update(self):
        super().update()
        self.check_light()

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group

#animals
class Bird(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/animals/bluebird/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_bird.Idle(self)
        self.flags['aggro'] = False
        self.health = 1
        self.AI = AI_bird.Idle(self)
        self.aggro_distance = [100,50]#at which distance is should fly away

    def knock_back(self,dir):
        pass

#NPCs
class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        if self.game_objects.world_state.state.get('reindeer', False):#if player has deafated the reindeer
            if not self.game_objects.player.states['Wall_glide']:#if player doesn't have wall yet (so it only enters once)
                self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game.game_objects.player.sprites[Wall_glide][0].copy())
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
            particle = getattr(particles, 'Circle')(self.hitbox.center, self.game_objects, distance=0, lifetime = -1, vel = {'linear':[7,15]}, dir='isotropic', scale=5, colour=[100,200,255,255], state = 'Circle_converge',gradient = 1)
            light = self.game_objects.lights.add_light(particle, colour = [100/255,200/255,255/255,255/255], radius = 20)
            particle.light = light#add light reference
            self.game_objects.cosmetics.add(particle)

    def give_light(self):#called when teleport shader is finished
        self.game_objects.lights.add_light(self.game_objects.player, colour = [200/255,200/255,200/255,200/255])
        self.game_objects.world_state.update_event('guide')

    def draw(self, target):#called in group
        self.shader_state.draw()
        pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

class Sahkar(NPC):#deer handler
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Busty_baker(NPC):#bartender
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_droplet':1}#itam+price
        text = self.dialogue.get_comment()
        self.random_conversation(text)

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Vendor', category = 'game_states_facilities', npc = self)

class MrSmith(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Smith', category = 'game_states_facilities', npc = self)

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
        self.game_objects.game.state_manager.enter_state(state_name = 'Bank', category = 'game_states_facilities', npc = self)

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
        self.game_objects.game.state_manager.enter_state(state_name = 'Conversation', npc = self)
        if self.game_objects.world_state.quests.get('lumberjack_omamori', False):#if the quest is running
            self.game_objects.quests_events.active_quests['lumberjack_omamori'].complete()

class Reindeer(Boss):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/boss/reindeer/',game_objects)
        self.image = self.sprites['idle_nice'][0]
        self.animation.play('idle_nice')
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 35, 45)

        self.currentstate = reindeer_states.Idle_nice(self)
        self.AI = reindeer_ai.AI(self)

        self.ability = 'air_dash_main'#the stae of image that will be blitted to show which ability that was gained
        self.attack_distance = [50, 10]
        self.attack = Hurt_box
        self.game_objects.lights.add_light(self, radius = 150)
        self.chase_speed = 2
        self.animation.framerate = 1/6

    def give_abillity(self):#called when reindeer dies
        self.game_objects.world_state.cutscenes_complete['Boss_deer_encounter'] = True#so not to trigger the cutscene again
        self.game_objects.player.states['Dash'] = True#append dash abillity to available states

class Butterfly(Flying_enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/boss/butterfly/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos,self.image.size)
        self.hitbox = self.rect.copy()
        self.AI = AI_butterfly.Idle(self)
        self.currentstate = states_butterfly.Idle(self)
        self.health =20

    def knock_back(self,dir):
        pass

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('butterfly_killed')

    def right_collision(self,block, type = 'Wall'):
        pass

    def left_collision(self,block, type = 'Wall'):
        pass

    def down_collision(self,block):
        pass

    def top_collision(self,block):
        pass

class Rhoutta_encounter(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('Sprites/enteties/boss/rhoutta/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 3
        self.attack_distance = [100,10]
        self.attack = Sword
        self.dmg = 0

    def dead(self):
        self.game_objects.game.state_manager.exit_state()
        self.game_objects.player.reset_movement()
        self.game_objects.game.state_manager.enter_state(state_name = 'Defeated_boss', category = cutscenes, page = 'Rhoutta_encounter')

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
        self.rect[2], self.rect[3] = size[0], size[1]
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
        super().__init__(entity.rect.center, entity.game_objects)
        self.image = entity.image
        self.image_copy = Fade_effect.image_copy

        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.center = entity.rect.center
        self.alpha = alpha

        self.true_pos = self.rect.topleft
        self.dir = entity.dir.copy()

    def update(self):
        self.alpha *= 0.9
        self.destroy()

    def draw(self, target):
        self.image_copy.clear(0,0,0,0)
        self.game_objects.shaders['motion_blur']['dir'] = [0.05, 0]
        self.game_objects.shaders['motion_blur']['quality'] = 3
        self.game_objects.game.display.render(self.image, self.image_copy, shader = self.game_objects.shaders['motion_blur'])#shader render

        self.game_objects.shaders['alpha']['alpha'] = self.alpha
        blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image_copy.texture, target, position = blit_pos, flip = self.dir[0] > 0, shader = self.game_objects.shaders['alpha'])#shader render

    def pool(game_objects):
        size = (96, 64)#player canvas size
        Fade_effect.image_copy = game_objects.game.display.make_layer(size)

    def destroy(self):
        if self.alpha < 10:
            self.kill()

    def release_texture(self):
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
        self.colour = (colour.g,colour.b,colour.a,15/parallax[0])
        self.shader_state = states_shader.Idle(self)

        layer1 = self.game_objects.game.display.make_layer(game_objects.game.window_size)#make an empty later
        layer1.clear(self.colour)
        self.image = layer1.texture#get the texture of the layer

    def release_texture(self):
        self.image.release()

    def update(self):
        self.shader_state.update()

    def draw(self, target):
        self.shader_state.draw()
        self.game_objects.game.display.render(self.image, target, shader = self.shader)#shader render

#Player movement abilities, handles them. Contains also spirit abilities
class Player_abilities():
    def __init__(self,entity):
        self.entity = entity
        self.spirit_abilities = {'Thunder': Horagalles_rage(entity),'Shield': Tjasolmais_embrace(entity),'Bow': Juksakkas_blessing(entity),'Wind': Bieggs_breath(entity),'Slow_motion': Beaivis_time(entity)}#abilities aila has
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

    def handle_input(self, value):#movement stuff
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

class Player_ability():#aila abilities
    def __init__(self,entity):
        self.entity = entity
        self.game_objects = entity.game_objects
        self.level = 1#upgrade pointer
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.animation.play('idle_1')

    def level_up(self):
        self.level += 1

    def activate(self,level):#for UI of Aila abilities
        self.animation.play('active_' + str(level))
        self.level = level

    def deactivate(self,level):#for UI of Aila abilities
        self.animation.play('idle_' + str(level))
        self.level = level

    def initiate(self):#called when using the ability
        pass

    def update(self):#called from gameplayHUD
        self.animation.update()
        self.currentstate.update()

    def reset_timer(self):
        pass

class Dash(Player_ability):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/abilities/Dash/',entity.game_objects)
        self.image = self.sprites['idle_1'][0]
        self.description = ['dash','free dash','invinsible dash','dash attack']

class Wall_glide(Player_ability):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/abilities/Wall_glide/',entity.game_objects)
        self.image = self.sprites['idle_1'][0]
        self.description = ['wall glide','free wall jumps','donno','donno']

class Double_jump(Player_ability):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/UI/abilities/Double_jump/',entity.game_objects)
        self.image = self.sprites['idle_1'][0]
        self.description = ['doulbe jump','free double jump','donno','donno']

class Horagalles_rage(Player_ability):#desolate dive:thunder god:
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/horagalles_rage/',entity.game_objects)
        self.description = ['thunder','hits one additional target','one additional damage','imba']

    def initiate(self, enemy_rect):
        thunder = Thunder(enemy_rect, self.entity.game_objects, lifetime =  1000)
        thunder.rect.midbottom = enemy_rect.midbottom
        thunder.hitbox = thunder.rect.copy()
        self.entity.projectiles.add(thunder)#add attack to group

class Tjasolmais_embrace(Player_ability):#makes the shield, water god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/tjasolmais_embrace/',entity.game_objects)
        self.description = ['shield','hits one additional target','one additional damage','imba']
        self.shield = None#-> higher level can reflect projectiles? or maybe hurt enemy?

    def shield_expire(self):#called when the shield is destroyed
        self.entity.movement_manager.remove_modifier('Tjasolmais_embrace')
        self.entity.damage_manager.remove_modifier('Tjasolmais_embrace')
        self.shield = None

    def sword(self):#called when aila swings the sword
        if self.shield: self.shield.kill()

    def initiate(self):#called when using the abilty
        if self.shield: self.shield.kill()    #kill the old one
        self.shield = Shield(self.entity)
        self.entity.movement_manager.add_modifier('Tjasolmais_embrace', entity = self.entity)
        self.entity.damage_manager.add_modifier('Tjasolmais_embrace', entity = self.entity)

        self.entity.projectiles.add(self.shield)

class Bieggs_breath(Player_ability):#force push
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/bieggs_breath/',entity.game_objects)
        self.health = 1
        self.description = ['wind','hard wind']

    def initiate(self):#called when using the ability
        if self.entity.dir[1] == 0:#left or right
            dir = self.entity.dir.copy()
        else:#up or down
            dir = [0,-self.entity.dir[1]]

        spawn = Wind(self.entity.rect.center, self.entity.game_objects, dir = dir)
        self.entity.game_objects.fprojectiles.add(spawn)

    def upgrade_ability(self):#called from upgrade menu
        self.level += 1
        if self.level == 2:
            self.health = 2

class Beaivis_time(Player_ability):#slow motion -> sun god: Beaiviáigi in sami
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/beaivis_time/',entity.game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/projectiles/beaivis_time/')
        self.duration = 10#slow motion duration, in time [whatever units]
        self.rate = 0.5#slow motion rate
        self.description = ['slow motion','slow motion but aila']
        self.channels = []

    def initiate(self):#called when using the ability from player states
        self.entity.game_objects.fprojectiles.add(Counter(self.entity, dir = (0,0), lifetime = self.duration))

    def counter(self):#called from counter if sucsesfully countered
        self.channels.append(self.entity.game_objects.sound.play_sfx(self.sounds['counter'][0], loop = -1, vol = 0.5))
        self.channels.append(self.entity.game_objects.sound.play_sfx(self.sounds['woosh'][0], vol = 0.5))

        self.game_objects.time_manager.modify_time(time_scale = self.rate, duration = self.duration)#sow motion
        self.game_objects.time_manager.modify_time(time_scale = 0, duration = 20)#freeze
        self.entity.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 20, scale = 0.9)
        self.entity.emit_particles(lifetime = 40, scale=3, colour=C.spirit_colour, fade_scale = 7, number_particles = 60 , gradient = 1)
        self.entity.game_objects.cosmetics.add(Slash(self.entity.hitbox.center,self.game_objects))#make a slash animation

        self.entity.currentstate.enter_state('Air_dash_pre')#what should the player do?
        self.game_objects.shader_render.append_shader('white_balance', temperature = 0.2)#change the tone of screen
        #self.game_objects.shader_render.append_shader('zoom', scale = 0.8)

        #maybe make attacks double the damage?
        #get spirit?
        #add particles, screen shaske, bloom? zoom in?
        #add echo FX, heart beat, slow pitch drop
        # ability symbol pulses
        #reposigion behind the enemy/projectile?
        #give free dash?
        #summon a phantom copy that repeats your last attack when time resumes.
        #upgrade, freeze enemy?

    def exit(self):
        self.game_objects.shader_render.remove_shader('white_balance')
        for channel in self.channels:
            self.entity.game_objects.sound.fade_sound(channel)

    def upgrade_ability(self):#called from upgrade menu
        self.entity.slow_motion = 1/self.rate#can make aila move normal speed

class Juksakkas_blessing(Player_ability):#arrow -> fetillity god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/UI/juksakkas_blessing/', entity.game_objects)
        self.level = 1#upgrade pointer
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

    def initiate(self, dir, time):#called when relasing the button
        self.entity.projectiles.add(Arrow(pos = self.entity.hitbox.topleft, game_objects = self.entity.game_objects, dir = dir, lifetime = 50, time = time))#add attack to group

#projectiles
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

    def pool(game_objects):
        Bouncy_balls.sprites = read_files.load_sprites_dict('Sprites/attack/projectile_1/',game_objects)

    def release_texture(self):
        pass

    def kill(self):#when lifeitme runs out or hit by aila sword
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    def take_dmg(self, dmg):#when hit by aila sword without purple stone
        self.velocity = [0,0]
        self.dmg = 0
        self.currentstate.handle_input('Death')
        self.game_objects.signals.emit('ball_killed')

    #platform collisions
    def right_collision(self, block, type = 'Wall'):
        self.hitbox.right = block.hitbox.left
        self.collision_types['right'] = True
        self.currentstate.handle_input(type)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self, block, type = 'Wall'):
        self.hitbox.left = block.hitbox.right
        self.collision_types['left'] = True
        self.currentstate.handle_input(type)
        self.velocity[0] = -self.velocity[0]

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def down_collision(self, block):
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
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 100)
        self.dir = kwarg.get('dir', [1, -1])
        amp = kwarg.get('amp', [5, 5])
        self.velocity = [-amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        self.velocity[1] += 0.1 * self.game_objects.game.dt#graivity

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
        amp = kwarg.get('amp', [5, 5])
        self.velocity = [-amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def pool(game_objects):
        Projectile_1.sprites = read_files.load_sprites_dict('Sprites/attack/projectile_1/',game_objects)

    def collision_platform(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.collision_platform(None)

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

class Hurt_box(Melee):#a hitbox that spawns
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = pygame.Rect(entity.rect.topleft, kwarg.get('size', [64, 64]))
        self.dmg = kwarg.get('dmg', 1)

    def update(self):
        self.lifetime -= self.game_objects.game.dt
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

class Counter(Melee):
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = self.entity.hitbox.copy()
        self.dmg = 0
        self.entity.flags['invincibility'] = True#make the player invincible

    def update(self):
        self.lifetime -= self.game_objects.game.dt
        self.destroy()

    def collision_enemy(self, collision_enemy):
        self.counter()

    def collision_projectile(self, eprojectile):
        self.counter()

    def counter(self):
        if self.flags['invincibility']: return#such that it only collides ones
        self.flags['invincibility'] = True
        self.entity.game_objects.timer_manager.start_timer(C.invincibility_time_player, self.entity.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.entity.abilities.spirit_abilities['Slow_motion'].counter()#slow motion

    def kill(self):
        super().kill()
        self.entity.abilities.spirit_abilities['Slow_motion'].exit()

    def draw(self, target):
        pass

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
        if collision_enemy.flags['invincibility']: return
        collision_enemy.take_dmg(self.dmg)
        collision_enemy.knock_back(self.dir)
        collision_enemy.emit_particles(dir = self.dir)
        #slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])#self.entity.cosmetics.add(slash)
        self.clash_particles(collision_enemy.hitbox.center, lifetime = 20, dir = random.randint(-180, 180))

    def clash_particles(self, pos, number_particles = 12, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, **kwarg)
            self.entity.game_objects.cosmetics.add(obj1)

class Aila_sword(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('Sprites/attack/aila_slash/',self.entity.game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/projectiles/aila_sword/')
        self.image = self.sprites['slash_1'][0]
        self.animation.play('slash_1')
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_sword.Slash_1(self)

        self.dmg = 1

        self.tungsten_cost = 1#the cost to level up to next level
        self.stones = {}#{'red': Red_infinity_stone([0,0], entity.game_objects, entity = self), 'green': Green_infinity_stone([0,0], entity.game_objects, entity = self), 'blue': Blue_infinity_stone([0,0],entity.game_objects, entity = self),'orange': Orange_infinity_stone([0,0],entity.game_objects, entity = self),'purple': Purple_infinity_stone([0,0], entity.game_objects, entity = self)}#gets filled in when pick up stone. used also for inventory
        self.swing = 0#a flag to check which swing we are at (0 or 1)
        self.stone_states = {'enemy_collision': states_sword.Stone_states(self), 'projectile_collision': states_sword.Stone_states(self), 'slash': states_sword.Stone_states(self)}#infinity stones can change these to do specific things

    def update_hitbox(self):#every frame from collisions
        hitbox_attr, entity_attr = self.direction_mapping[tuple(self.dir)]#self.dir is set in states_sword
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate.update_rect()

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with projectile
        if eprojectile.flags['invincibility']: return
        eprojectile.flags['invincibility'] = True
        self.entity.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, eprojectile.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.stone_states['projectile_collision'].projectile_collision(eprojectile)

    def collision_enemy(self, collision_enemy):
        self.currentstate.sword_jump()#only down sword will give velocity up
        if collision_enemy.take_dmg(self.dmg):#if damage was taken
            self.entity.hitstop_states.enter_state('Stop', lifetime = 5)#hitstop to sword vielder
            collision_enemy.hitstop_states.enter_state('Stop', lifetime = 10, call_back = lambda: collision_enemy.knock_back(self.dir))#hitstop to enemy, with knock back after hittop
            collision_enemy.emit_particles(dir = self.dir)#, colour=[255,255,255,255])
            self.clash_particles(collision_enemy.hitbox.center)
            #self.game_objects.sound.play_sfx(self.sounds['sword_hit_enemy'][0], vol = 0.04)

            collision_enemy.currentstate.handle_input('sword')
            self.stone_states['enemy_collision'].enemy_collision()

    def clash_particles(self, pos, number_particles=12):
        angle = random.randint(-180, 180)#the erection anglex
        color = [255, 255, 255, 255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, distance = 0, lifetime = 40, vel = {'linear':[7,14]}, dir = angle, scale = 1.2, fade_scale = 5, colour = color, state = 'Idle')
            self.entity.game_objects.cosmetics.add(obj1)

    def level_up(self):#called when the smith imporoves the sword
        self.entity.inventory['Tungsten'] -= self.tungsten_cost
        self.dmg *= 1.2
        self.tungsten_cost += 2#1, 3, 5 tungstes to level up

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

class Arrow(Projectiles):#should it be called seed?
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Arrow.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100

        self.dir = kwarg.get('dir', [1, 0])
        normalise = (self.dir[0] ** 2 + self.dir[1] ** 2)**0.5
        amp = kwarg.get('time', 0)/50#50 is the charge duration, how long one sohuld press to reach max speed
        amp = min(amp, 1)#limit the max charge to 1

        self.velocity = [amp * self.dir[0] * 20 / normalise, amp * self.dir[1] * 20 / normalise]
        self.seed_spawner = seeds.SeedSpawner(self)

        self.once = False

        self.acceleration = [0, 0.1]
        self.friction = [0.01, 0.01]
        self.max_vel = [10, 10]

    def update_vel(self):#called from hitsop_states
        self.velocity[1] += self.slow_motion*self.game_objects.game.dt*(self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1],self.max_vel[1]*self.game_objects.game.dt)#set a y max speed#
        self.velocity[0] += self.slow_motion*self.game_objects.game.dt*(self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def update(self):
        super().update()
        self.update_vel()
        self.angle = self._get_trajectory_angle()
        self.emit_particles(lifetime = 50, dir = self.dir, vel = {'linear': [self.velocity[0] * 0.1, self.velocity[1] * 0.1]}, scale = 0.5, fade_scale = 5)

    def emit_particles(self, type = 'Circle', **kwarg):
        obj1 = getattr(particles, type)(self.hitbox.center, self.game_objects, **kwarg)
        self.game_objects.cosmetics.add(obj1)

    def _get_trajectory_angle(self):
        return math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0)#shader render

    def pool(game_objects):
        Arrow.sprites = read_files.load_sprites_dict('Sprites/attack/arrow/', game_objects)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        self.kill()

    def collision_interactables(self,interactable):#collusion interactables
        pass

    def collision_interactables_fg(self, interactable):#collusion interactables_fg: e.g. twoDliquid
        if self.once: return
        self.once = True
        interactable.seed_collision(self)
        self.velocity = [0,0]
        self.kill()

    def collision_enemy(self,collision_enemy):
        self.kill()

    def right_collision(self, block, type = 'Wall'):
        self.collision_platform([1, 0], block)

    def left_collision(self, block, type = 'Wall'):
        self.collision_platform([-1, 0], block)

    def down_collision(self, block):
        self.collision_platform([0, -1], block)

    def top_collision(self, block):
        self.collision_platform([0, 1], block)

    def collision_platform(self, dir, block):
        self.velocity = [0,0]
        if self.once: return
        self.once = True
        self.seed_spawner.spawn_seed(block, dir)
        self.kill()

class Wind(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Wind.image
        self.rect = pygame.Rect(pos[0], pos[1], self.image.texture.width, self.image.texture.height)
        self.hitbox = self.rect.copy()
        self.dmg = 0

        self.time = 0

        self.dir = kwarg.get('dir', [1,0])
        self.velocity = [self.dir[0] * 10, self.dir[1] * 10]

    def collision_platform(self, platform):
        self.velocity = [0,0]
        self.kill()

    def pool(game_objects):
        size = [64, 64]
        Wind.image = game_objects.game.display.make_layer(size)

    def collision_enemy(self, collision_enemy):#if hit something
        self.velocity = [0,0]
        collision_enemy.velocity[0] = self.dir[0]*40#abs(push_strength[0])
        collision_enemy.velocity[1] = -1
        self.kill()

    def update(self):
        self.time += self.game_objects.game.dt
        self.lifetime -= self.game_objects.game.dt
        self.destroy()

    def draw(self, target):
        self.game_objects.shaders['up_stream']['dir'] = self.dir
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['up_stream'])#shader render

class Shield(Projectiles):#a protection shield
    def __init__(self, entity, **kwarg):
        super().__init__(entity.hitbox.topleft, entity.game_objects)
        self.entity = entity

        self.size = Shield.size
        self.empty = Shield.empty
        self.noise_layer = Shield.noise_layer
        self.screen_layer = Shield.screen_layer
        self.image = Shield.image

        self.rect = pygame.Rect(entity.hitbox.center, self.size)
        self.hitbox = self.rect.copy()
        self.reflect_rect = self.hitbox.copy()

        self.time = 0
        self.health = kwarg.get('health', 1)
        self.lifetime = kwarg.get('lifetime', 100)
        self.die = False
        self.progress = 0

    def take_damage(self, dmg):#called when entity takes damage
        if self.flags['invincibility']: return
        self.health -= dmg

        self.flags['invincibility'] = True
        if self.health > 0:#TODO make it red momentary or something to indicate that it too damage
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        else:
            self.game_objects.timer_manager.start_timer(100, self.time_out)#adds a timer to timer_manager and sets self.invincible to false after a while
            #TODO make it blink or something to indicate that it will die soon

    def time_out(self):#called when general timer it count down
        self.kill()

    def update(self):
        self.time += self.entity.game_objects.game.dt
        if self.time > self.lifetime:
            self.die = True
            self.progress += self.entity.game_objects.game.dt*0.005
            if self.progress >= 1:
                self.kill()
        self.update_pos()

    def update_pos(self):
        self.true_pos = [int(self.entity.hitbox.center[0] - self.game_objects.camera_manager.camera.scroll[0] - 90*0.5),int(self.entity.hitbox.center[1] - self.game_objects.camera_manager.camera.scroll[1]- 90*0.5)]
        self.rect.topleft = self.hitbox.center

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.001
        self.game_objects.shaders['noise_perlin']['scroll'] = [0, 0]
        self.game_objects.shaders['noise_perlin']['scale'] = [3,3]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #cut out the screen
        self.reflect_rect.bottomleft = [self.hitbox.topleft[0], 640 - self.hitbox.topleft[1] + 90 - 10]
        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.screen_layer, section = self.reflect_rect)

        self.game_objects.shaders['shield']['TIME'] = self.time*0.001
        self.game_objects.shaders['shield']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['shield']['screen_tex'] = self.screen_layer.texture

        if not self.die:#TODO
            self.game_objects.game.display.render(self.empty.texture, self.image, shader = self.game_objects.shaders['shield'])#shader render
            self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = self.hitbox.topleft)#shader render
        else:
            self.game_objects.shaders['dissolve']['dissolve_texture'] = self.noise_layer.texture
            self.game_objects.shaders['dissolve']['dissolve_value'] = max(1 - self.progress,0)
            self.game_objects.shaders['dissolve']['burn_size'] = 0.0
            self.game_objects.shaders['dissolve']['burn_color'] = [0.39, 0.78, 1,0.7]

            self.game_objects.game.display.render(self.empty.texture, self.image, shader = self.game_objects.shaders['shield'])#shader render
            self.game_objects.game.display.render(self.image.texture, self.game_objects.game.screen, position = self.hitbox.topleft, shader = self.game_objects.shaders['dissolve'])#shader render

    def pool(game_objects):
        Shield.size = [90, 90]
        Shield.empty = game_objects.game.display.make_layer(Shield.size)
        Shield.noise_layer = game_objects.game.display.make_layer(Shield.size)
        Shield.screen_layer = game_objects.game.display.make_layer(Shield.size)
        Shield.image = game_objects.game.display.make_layer(Shield.size)

    def kill(self):
        super().kill()
        self.entity.abilities.spirit_abilities['Shield'].shield_expire()

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        pass

    def collision_platform(self, collision_plat):#collision platform, called from collusoin_block
        pass

#things player can pickup
class Heart_container(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/items/heart_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'A heart container'

    def update_vel(self):
        self.velocity[1] = 3*self.game_objects.game.dt

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
        self.velocity[1]=3*self.game_objects.game.dt

    def player_collision(self,player):
        player.max_spirit += 1
        #a cutscene?
        self.kill()

class Soul_essence(Loot):#genkidama
    def __init__(self, pos, game_objects, ID_key = None):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/enteties/items/soul_essence/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'An essence container'#for shops
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def player_collision(self, player):
        player.backpack.inventory.add('soul_essence')
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

class Amber_droplet(Enemy_drop):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Amber_droplet.sprites
        self.sounds = Amber_droplet.sounds

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
        name = self.__class__.__name__.lower()
        tot_amber = player.backpack.inventory.get_quantity(name)
        self.game_objects.UI.hud.update_money(tot_amber)

    def pool(game_objects):#all things that should be saved in object pool
        Amber_droplet.sprites = read_files.load_sprites_dict('Sprites/enteties/items/amber_droplet/',game_objects)
        Amber_droplet.sounds = read_files.load_sounds_dict('audio/SFX/enteties/items/amber_droplet/')

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
        if self.game_objects.player.backpack.inventory.get_quantity('bone') <= 0: return#if we don't have bones
        self.game_objects.player.backpack.inventory.remove('bone')
        self.game_objects.player.backpack.map.save_bone(map = self.game_objects.map.level_name, point = self.game_objects.camera_manager.camera.scroll)
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
        if self.game_objects.player.backpack.inventory.get_quantity('heal_item') < 0: return
        self.game_objects.player.backpack.inventory.remove('heal_item')
        self.game_objects.player.heal(1)

    def pool(game_objects):#all things that should be saved in object pool: #obj = cls.__new__(cls)#creatate without runing initmethod
        Heal_item.sprites = read_files.load_sprites_dict('Sprites/enteties/items/heal_item/',game_objects)
        Heal_item.sounds = read_files.load_sounds_dict('audio/SFX/enteties/items/heal_item/')

    def release_texture(self):#stuff that have pool shuold call this
        pass

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
        player.backpack.inventory.add('tungsten')

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
        player.backpack.necklace.inventory[type(self).__name__] = self
        self.entity = player

    def handle_press_input(self,input):
        pass

    def detach(self):
        self.animation.play('idle')

    def attach(self):
        self.animation.play('equip')

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
        self.entity.damage_manager.add_modifier('Half_dmg')

    def detach(self):
        super().detach()
        self.entity.damage_manager.remove_modifier('Half_dmg')

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
        self.quest = kwarg.get('quest', None)

    def equipped(self):#an update that should be called when equppied
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

    def interact(self, player):
        super().interact(player)
        self.game_objects.quests_events.initiate_quest(self.quest.capitalize(), item = 'Loot_magnet')

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

class Indincibillity(Omamori):#extends the invincibillity time
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Runspeed(Omamori):#increase the runs speed
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Dashpeed(Omamori):#decrease the dash cooldown?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Shields(Omamori):#autoamtic shield that negates one damage, if have been outside combat for a while?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Wallglue(Omamori):#to make aila stick to wall, insead of gliding?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Hover(Omamori):#If holding jump button, make a small hover
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

class Infinity_stones(Interactable_item):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sword = kwarg.get('entity', None)
        self.description = ''

    def set_pos(self, pos):#for inventory
        self.rect.center = pos

    def reset_timer(self):
        pass

    def attach(self, player):#called from sword when balcksmith attached the stone
        pass

    def pickup(self, player):
        super().pickup(player)
        self.attach(player)
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
        self.sword.dmg *= 1.1

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

    def attach(self, player):
        player.sword.stone_states['slash'].enter_state('Slash', 'slash')

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

    def attach(self, player):
        player.sword.stone_states['enemy_collision'].enter_state('Enemy_collision', 'enemy_collision')

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

    def attach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y, 80, 40)
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

    def attach(self, player):
        player.sword.stone_states['projectile_collision'].enter_state('Projectile_collision', 'projectile_collision')

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

class Dusts(Animatedentity):#dust particles when doing things
    def __init__(self, pos, game_objects, dir = [1,0], state = 'one'):
        super().__init__(pos, game_objects)
        self.sprites = Dusts.sprites
        self.image = self.sprites[state][0]
        self.animation.play(state)
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.dir = dir
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Dusts.sprites = read_files.load_sprites_dict('Sprites/GFX/dusts/', game_objects, flip_x = True)

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
        self.timer += self.game_objects.game.dt
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
        self.animation.play('slash_' + state)
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

class Bubble_source(Interactable):#the thng that spits out bubbles in cave HAWK TUAH!
    def __init__(self, pos, game_objects, bubble, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/bubble_source/', game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/bubble_source/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()
        self.spawn_timer = prop.get('spawnrate', 180)
        #self.spawn_timer = 180

        self.bubble = bubble#the bubble is in platform, so the reference is sent in init
        self.prop = prop
        #self.time = random.randint(0, 10)
        self.time = -1 * prop.get('init_delay', random.randint(0, 50))

    def group_distance(self):
        pass

    def draw(self, target):
        pass

    def update(self):
        super().update()
        self.time += self.game_objects.game.dt
        if self.time > self.spawn_timer:
            self.game_objects.sound.play_sfx(self.sounds['spawn'][random.randint(0, 1)], vol = 0.3)
            bubble = self.bubble([self.rect.centerx, self.rect.top], self.game_objects, **self.prop)
            #self.game_objects.dynamic_platforms.add(bubble)
            self.game_objects.platforms.add(bubble)
            #self.time = random.randint(0, 10)
            self.time = 0

class Crystal_source(Interactable):#the thng that spits out crystals in crystal mines
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/crystal_source/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.time = 0
        self.frequency = kwarg.get('frequency', 15)
        self.kwarg = kwarg

    def group_distance(self):
        pass

    def update(self):
        super().update()
        self.time += self.game_objects.game.dt
        if self.time > self.frequency:
            crystal = Projectile_1(self.rect.center, self.game_objects, **self.kwarg)
            self.game_objects.eprojectiles.add(crystal)
            self.time = 0

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
        self.game_objects.game.state_manager.enter_state(state_name = 'Conversation', npc = self)

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

        self.item = item
        self.quest = quest

        self.interacted = self.game_objects.world_state.quests.get(quest, False)
        self.dialogue = dialogue.Dialogue_interactable(self, quest)#handles dialoage and what to say
        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self)

    def buisness(self):#enters after conversation
        item = getattr(sys.modules[__name__], self.item.capitalize())(self.rect.center, self.game_objects, quest = self.quest)#make a class based on the name of the newstate: need to import sys
        self.game_objects.loot.add(item)

class Air_dash_statue(Interactable):#interact with it to get air dash
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/statues/air_dash_statue/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.interacted = self.game_objects.player.states.get('Air_dash', False)

        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self, colour = [0,0,0,100])
        self.text = 'dash in air'

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def interact(self):#when player press t/y
        if self.interacted: return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.game_objects.player.states['Air_dash'] = True#give ability
        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites['air_dash_main'][0], text = self.text, callback = self.on_exit)

    def on_exit(self):#called when eiting the blit_image_text state
        self.game_objects.player.currentstate.handle_input('Pray_post')#needed when picked up Interactable_item

class Thunder_dive_statue(Interactable):#interact with it to upgrade horagalles rage
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/statues/thunder_dive_statue/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        ability = self.game_objects.player.abilities.spirit_abilities.get('Thunder', False)
        self.interacted = ability and ability.level == 2#if level 2, inteeracted = True

        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self, colour = [0, 0, 0, 100])
        self.text = 'thunder dive in directions'

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def interact(self):#when player press t/y
        if self.interacted: return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        ability = self.game_objects.player.abilities.spirit_abilities['Thunder'].level_up()
        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites['thunder_main'][0], text = self.text, callback = self.on_exit)

    def on_exit(self):#called when eiting the blit_image_text state
        self.game_objects.player.currentstate.handle_input('Pray_post')#needed when picked up Interactable_item

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
        player.backpack.map.save_safespawn(self.position)

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
        player.take_dmg()
        self.interacted = True

    def player_transport(self, player):#transports the player to safe position
        if player.health > 1:#if about to die, don't transport to safe point
            self.game_objects.game.state_manager.enter_state(state_name = 'Safe_spawn_1')

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
        pass
        #self.group_distance()

    def player_movement(self, player):#the movement aila does when colliding
        if self.rect[3] > self.rect[2]:#if player was trvelling horizontally, enforce running in that direction
            player.currentstate.enter_state('Run_main')#infstaed of idle, should make her move a little dependeing on the direction
            player.acceleration[0] = C.acceleration[0]
        else:#vertical travelling
            if player.velocity[1] < 0:#up
                player.velocity[1] = -10
            else:#down
                pass

    def player_collision(self, player):
        self.player_movement(player)
        self.game_objects.load_map(self.game_objects.game.state_manager.state_stack[-1], self.destination, self.spawn)#nned to send previous state so that we can update and render for exampe gameplay or title screeen while fading
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
        self.game_objects.load_map(self.game_objects.game.state_manager.state_stack[-1],self.destination, self.spawn)

class Shade_trigger(Interactable):#it changes the colourof shade screen to a new colour specified by self.new_colour
    def __init__(self, pos, game_objects, size, colour = pygame.Color(0,0,0,0)):
        super().__init__(pos, game_objects)
        self.new_colour = [colour.g,colour.b,colour.a]
        self.light_colour = self.game_objects.lights.ambient[0:3]
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self):
        pass

    def player_collision(self, player):#player collision
        self.game_objects.lights.ambient = self.new_colour + [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]
        for layer in self.layers:
            layer.shader_state.handle_input('mix_colour')

    def player_noncollision(self):#when player doesn't collide
        self.game_objects.lights.ambient = self.light_colour + [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]
        for layer in self.layers:
            layer.shader_state.handle_input('idle')

    def add_shade_layers(self, layers):#called from map loader
        self.layers = layers
        for layer in layers:
            layer.new_colour = self.new_colour + [layer.colour[-1]]
            layer.bounds = self.rect

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
        self.flags = {'invincibility': False}

    def take_dmg(self,projectile):
        if self.flags['invincibility']: return
        #projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.flags['invincibility']  = True

        if self.health > 0:
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            self.currentstate.handle_input('Once', animation_name = 'hurt', next_state = 'Idle')
            #self.shader_state.handle_input('Hurt')#turn white
        else:#death
            self.currentstate.handle_input('Once', animation_name = 'interact', next_state = 'Interacted')
            self.game_objects.enemies.add(Maggot(self.rect.center,self.game_objects))

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

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
        if self.flags['invincibility']: return
        self.flags['invincibility'] = True
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

class Loot_containers(Interactable):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/' + type(self).__name__.lower() + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom
        self.shader_state = states_shader.Idle(self)

        self.health = 3
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.flags = {'invincibility':False}

        if state:
            self.currentstate = states_basic.Interacted(self)
            self.flags['invincibility'] = True

    def update(self):
        super().update()
        self.shader_state.update()

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def loots(self):#this is called when the opening animation is finished
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop, self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def take_dmg(self,projectile):
        if self.flags['invincibility']: return
        self.game_objects.sound.play_sfx(self.sounds['hit'][0], vol = 0.2)
        projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.flags['invincibility'] = True
        self.shader_state.handle_input('Hurt', colour = (1,1,1,0), direction = [1,0.5])
        self.hit_loot()

        if self.health > 0:
            self.currentstate.handle_input('Hurt')
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        else:
            self.currentstate.handle_input('Opening')
            self.game_objects.world_state.state[self.game_objects.map.level_name]['loot_container'][self.ID_key] = True#write in the state dict that this has been picked up

    def hit_loot(self):
        for i in range(0, random.randint(1,3)):
            obj = Amber_droplet(self.hitbox.midtop, self.game_objects)
            self.game_objects.loot.add(obj)

class Chest(Loot_containers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/chest/')
        self.inventory = {'Amber_droplet':3}

class Chest_2(Loot_containers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/chest/')
        self.inventory = {'Amber_droplet':1}

    def hit_loot(self):
        pass

class Amber_tree(Loot_containers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/amber_tree/')
        self.inventory = {'Amber_droplet':3}

class Amber_rock(Loot_containers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/amber_rock/')
        self.inventory = {'Amber_droplet':3}

class Door(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/door/')
        self.sprites=read_files.load_sprites_dict('Sprites/animations/Door/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        self.game_objects.sound.play_sfx(self.sounds['open'][0], vol = 0.2)
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
        self.currentstate = states_savepoint.Idle(self)

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.game_objects.player.backpack.map.save_savepoint(map =  self.map, point = self.init_cord)
        self.currentstate.handle_input('active')
        self.game_objects.cosmetics.add(Logo_loading(self.game_objects))

class Inorinoki(Interactable):#the place where you trade soul essence for spirit or heart contrainer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/inorinoki/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def interact(self):#when player press t/y
        self.game_objects.game.state_manager.enter_state(state_name = 'Soul_essence', category = 'game_states_facilities')

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
        if self.game_objects.player.backpack.inventory.get_quantity('amber_droplet') > self.cost:
            self.game_objects.player.backpack.inventory.remove('amber_droplet', self.cost)
            self.locked = False
            Fast_travel.cost *= 5#increase by 5 for every unlock
            self.game_objects.backpack.map.save_travelpoint(self.map,self.init_cord)
            return True
        else:
            return False

    def interact(self):#when player press t/y
        if self.locked:
            self.game_objects.game.state_manager.enter_state(state_name = 'Fast_travel_unlock', category = 'game_states_facilities', fast_travel = self)
        else:
            self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
            self.game_objects.game.state_manager.enter_state(state_name = 'Fast_travel_menu', category = 'game_states_facilities')

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
        self.game_objects.game.state_manager.enter_state(state_name = 'Rhoutta_encounter', category = 'cutscenes')

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
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/light_crystals/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.flags = {'invincibility': False}

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        projectile.clash_particles(self.hitbox.center)
        self.flags['invincibility'] = True
        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        self.currentstate.handle_input('Transform')
        self.game_objects.lights.add_light(self)#should be when interacted state is initialised and not on taking dmg

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

class Fireplace(Interactable):
    def __init__(self, pos, game_objects, on = False):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('audio/SFX/enteties/interactables/fireplace/')
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
        self.light_sources.append(self.game_objects.lights.add_light(self, flicker = True, radius = 50))
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

class Door_inter(Interactable): #game object for itneracting with locked door
    def __init__(self, pos, game_objects, door_obj):
        super().__init__(pos, game_objects)
        self.door = door_obj
        self.rect = door_obj.rect.copy()
        self.rect = self.rect.inflate(5,0)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        if type(self.door.currentstate).__name__ == 'Erect':
            if self.game_objects.player.backpack.inventory.get_quantity(self.door.key):
                self.door.currentstate.handle_input('Transform')
                if self.sfx: self.play_sfx()
            else:
                self.door.shake()

    def player_collision(self, player):#player collision
        pass

    def update(self):
        pass

    def draw(self, target):
        pass

    def release_texture(self):
        pass

class Lever(Interactable):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/lever/', game_objects)
        self.image = self.sprites['off'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.ID_key = kwarg.get('ID', None)#an ID to match with the reference (gate or platform etc) and an unique ID key to identify which item that the player is intracting within the world
        self.flags = {'invincibility': False}
        if self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'].get(self.ID_key, False) or kwarg.get('on', False):
            self.currentstate = states_lever.On(self)
        else:
            self.currentstate = states_lever.Off(self)

        self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key] = kwarg.get('on', False)

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        self.flags['invincibility'] = True
        self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while

        projectile.clash_particles(self.hitbox.center)

        self.currentstate.handle_input('Transform')
        self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key] = not self.game_objects.world_state.state[self.game_objects.map.level_name]['lever'][self.ID_key]#write in the state dict that this has been picked up
        self.reference.currentstate.handle_input('Transform')

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def add_reference(self, reference):#called from map loader
        self.reference = reference
        if type(self.currentstate).__name__ == 'On':
            self.reference.currentstate.handle_input('On')#erect
        else:
            self.reference.currentstate.handle_input('Off')#down

class Shadow_light_lantern(Interactable):#emits a shadow light upon interaction. Shadow light inetracts with dark forest enemy and platofrm
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/shadow_light_lantern/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.light_sources = []
        if kwarg.get('on', False):
            self.make_light()

    def interact(self):#when player press t/y
        if not self.light_sources:
            self.make_light()
        else:
            for light in self.light_sources:
                self.game_objects.lights.remove_light(light)
            self.light_sources = []

    def make_light(self):
        self.light_sources.append(self.game_objects.lights.add_light(self, shadow_interact = False, colour = [100/255,175/255,255/255,255/255],flicker=True,radius = 300))
        self.light_sources.append(self.game_objects.lights.add_light(self, radius = 250, colour = [100/255,175/255,255/255,255/255],flicker=True))
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [100/255,175/255,255/255,255/255],radius = 200))

#status effects (like wet)
class Status():#like timers, but there is an effect during update
    def __init__(self, entity, duration, callback = None):
        self.entity = entity
        self.duration = duration
        self.callback = callback

    def activate(self):#add timer to the entity timer list
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)

    def update(self):
        self.lifetime -= self.entity.game_objects.game.dt
        if self.lifetime < 0:
            self.deactivate()

class Wet_status(Status):#"a wet status". activates when player baths, and spawns particles that drops from player
    def __init__(self,entity, duration):
        super().__init__(entity, duration)
        self.spawn_frequency = 5#how often to spawn particle
        self.time = 0

    def activate(self, water_tint):#called when aila bathes (2D water)
        self.lifetime = self.duration#reset the duration
        self.water_tint = water_tint
        self.drop()
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.entity.timers.append(self)

    def update(self):
        super().update()
        self.time += self.entity.game_objects.game.dt
        if self.time > self.spawn_frequency:
            self.time = 0
            self.drop()

    def drop(self):
        pos = [self.entity.hitbox.centerx + random.randint(-5,5), self.entity.hitbox.centery + random.randint(-5,5)]
        obj1 = particles.Circle(pos, self.entity.game_objects, lifetime = 50, dir = [0, -1], colour = [self.water_tint[0]*255, self.water_tint[1]*255, self.water_tint[2]*255, 255], vel = {'gravity': [0, -1]}, gravity_scale = 0.2, fade_scale = 2, gradient=0)
        self.entity.game_objects.cosmetics.add(obj1)
