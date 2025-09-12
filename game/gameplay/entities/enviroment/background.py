import pygame
from engine.utils import read_files
from gameplay.entities.base.static_entity import StaticEntity
from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.states import states_blur, states_shader
#parallax things and background visuals

class BgBlock(StaticEntity):
    def __init__(self, pos, game_objects, img, parallax, live_blur = False):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.layers = None  # Initialize layer to None
        self.image = self.game_objects.game.display.surface_to_texture(img)
        self.rect[2] = self.image.width
        self.rect[3] = self.image.height

        if self.parallax[0] < 1:
            self.blur_radius = min(1/self.parallax[0], 10)#set a limit to 10. Bigger may cause performance issue
        else:
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
            self.layers = self.game_objects.game.display.make_layer(self.image.size)# Make an empty layer
            self.game_objects.game.display.use_alpha_blending(False)#remove thr black outline
            self.game_objects.game.display.render(self.image, self.layers, shader = shader)  # Render the image onto the layer
            self.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
            self.image.release()
            self.image = self.layers.texture  # Get the texture of the layer

    def draw(self, target):
        self.blurstate.set_uniform()#zsets the blur radius
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)  # Shader render

    def release_texture(self):  # Called when .kill() and when emptying the group
        self.image.release()
        if self.layers:  # Release layer if it exists, used for thre blurring
            self.layers.release()

class BgFade(BgBlock):
    def __init__(self, pos, game_objects, img, parallax, positions, ID):
        super().__init__(pos, game_objects, img, parallax)
        self.shader_state = states_shader.Idle(self)
        self.make_hitbox(positions, pos)
        self.interacted = False
        self.sounds = read_files.load_sounds_list('assets/audio/sfx/bg_fade/')
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

    def update_render(self, dt):
        self.shader_state.update_render(dt)

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

class BgAnimated(AnimatedEntity):
    def __init__(self, game_objects, pos, sprite_folder_path, parallax = (1,1)):
        super().__init__(pos,game_objects)
        self.sprites = {'idle': read_files.load_sprites_list(sprite_folder_path, game_objects)}
        self.image = self.sprites['idle'][0]
        self.parallax = parallax

    def update(self, dt):
        self.animation.update(dt)

    def reset_timer(self):#animation need it
        pass            

#shaders based
class Beam(StaticEntity):
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size).texture
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.parallax = parallax
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.1

    def draw(self, target):
        self.game_objects.shaders['beam']['TIME'] = self.time
        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['beam'])#shader render

class Sky(StaticEntity):
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

    def update(self, dt):
        self.time += dt

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
        self.game_objects.shaders['cloud']['u_resolution'] = self.size

        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['cloud'])

class Waterfall(StaticEntity):
    def __init__(self, pos, game_objects, parallax, size, layer_name):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.layer_name = layer_name

        self.size = size
        self.empty = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        self.blur_layer = game_objects.game.display.make_layer(size)
        self.time = 5*100#offset the time

        sounds = read_files.load_sounds_dict('assets/audio/sfx/environment/waterfall/')
        self.channel = self.game_objects.sound.play_sfx(sounds['idle'][0], loop = -1)
        self.set_volume()

    def release_texture(self):
        self.empty.release()
        self.noise_layer.release()
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

    def update(self, dt):
        self.time += dt * 0.01
        self.set_volume()

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.001
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [70,20]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        screen_copy = self.game_objects.game.screen_manager.get_screen(layer = self.layer_name, include = True)#make a copy of the screen

        #water
        self.game_objects.shaders['waterfall']['refraction_map'] = self.noise_layer.texture
        self.game_objects.shaders['waterfall']['water_mask'] = self.noise_layer.texture
        self.game_objects.shaders['waterfall']['SCREEN_TEXTURE'] = screen_copy.texture
        self.game_objects.shaders['waterfall']['TIME'] = self.time * 0.5
        self.game_objects.shaders['waterfall']['texture_size'] = self.size

        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['waterfall']['section'] = [blit_pos[0],blit_pos[1],self.size[0],self.size[1]]

        if self.parallax[0] == 1:#TODO, blue state #don't blur if there is no parallax
            self.game_objects.game.display.render(self.empty.texture, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['waterfall'])
        else:
            self.blur_layer.clear(0, 0, 0, 0)
            self.game_objects.shaders['blur']['blurRadius'] = 1/self.parallax[0]#set the blur redius
            self.game_objects.game.display.render(self.empty.texture, self.blur_layer, shader = self.game_objects.shaders['waterfall'])
            self.game_objects.game.display.render(self.blur_layer.texture, target, position = blit_pos, shader = self.game_objects.shaders['blur'])

class Reflection(StaticEntity):#water, e.g. village
    def __init__(self, pos, game_objects, parallax, size, layer_name, **kwarg):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.offset = int(kwarg.get('offset', 10))
        self.squeeze = 1
        self.reflect_rect = pygame.Rect(self.rect.left, self.rect.top, size[0], size[1]/self.squeeze)
        self.layer_name = layer_name

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

        sounds = read_files.load_sounds_dict('assets/audio/sfx/environment/river/')
        self.channel = self.game_objects.sound.play_sfx(sounds['idle'][0], loop = -1, vol = 0.2)

    def release_texture(self):#called when .kill() and empty group
        self.empty.release()
        self.noise_layer.release()
        self.water_noise_layer.release()
        self.blur_layer.release()
        self.screen_copy.release()
        self.channel.fadeout(300)

    def update_render(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        #noise
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [10,10]#"standard"
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['noise_perlin']['scale'] = [10,80]# make it elongated along x, and short along y
        self.game_objects.game.display.render(self.empty.texture, self.water_noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        screen_copy = self.game_objects.game.screen_manager.get_screen(layer = self.layer_name, include = False)

        #water
        self.game_objects.shaders['water_perspective']['noise_texture'] = self.noise_layer.texture
        self.game_objects.shaders['water_perspective']['noise_texture2'] = self.water_noise_layer.texture
        self.game_objects.shaders['water_perspective']['TIME'] = self.time
        self.game_objects.shaders['water_perspective']['SCREEN_TEXTURE'] = screen_copy.texture#stuff to reflect
        self.game_objects.shaders['water_perspective']['water_speed'] = self.water_speed
        self.game_objects.shaders['water_perspective']['water_albedo'] = self.colour
        self.game_objects.shaders['water_perspective']['texture_parallax'] = self.texture_parallax
        self.game_objects.shaders['water_perspective']['water_texture_on'] = self.water_texture_on

        self.reflect_rect.bottomleft = [int(self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]), int(-self.offset + self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1])]# the part to cut
        blit_pos = [int(self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]), int(self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.shaders['water_perspective']['section'] = [self.reflect_rect[0],self.reflect_rect[1],self.reflect_rect[2],self.reflect_rect[3]]

        #final rendering -> tmporary fix TODO: there is a small flickering of the refected screen. This is cased by the camera stop, which isn't making it 100 % stationary. It makes the scroll go up and down by a pixel
        if self.parallax[0] == 1:#don't blur if there is no parallax            
            self.game_objects.game.display.render(self.empty.texture, target, position = blit_pos, section = self.reflect_rect, scale = [1, self.squeeze], shader = self.game_objects.shaders['water_perspective'])
        else:
            self.game_objects.shaders['blur']['blurRadius'] = 1/self.parallax[0]#set the blur redius
            self.game_objects.game.display.render(self.noise_layer.texture, self.blur_layer, shader = self.game_objects.shaders['water_perspective'])
            self.game_objects.game.display.render(self.blur_layer.texture, target, position = blit_pos, section = self.reflect_rect, scale = [1, self.squeeze], shader = self.game_objects.shaders['blur'])

class GodRaysRadial(StaticEntity):
    def __init__(self, pos, game_objects, parallax, size, **properties):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.image = game_objects.game.display.make_layer(size).texture
        self.shader = game_objects.shaders['rays_radial']
        self.shader['resolution'] = self.game_objects.game.window_size
        self.time = 0
        self.colour = properties.get('colour',(1.0, 0.9, 0.65, 0.6))#colour
        self.edge_falloff_distance = properties.get('edge_falloff_distance',0.3)

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        self.shader['edge_falloff_distance'] = self.edge_falloff_distance
        self.shader['time'] = self.time
        self.shader['size'] = self.image.size
        self.shader['color'] = self.colour

        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render

class GodRays(StaticEntity):
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

    def update(self, dt):
        self.time += dt * 0.1

    def draw(self, target):
        self.shader['angle'] = self.angle
        self.shader['position'] = self.position
        self.shader['falloff'] = self.falloff
        self.shader['time'] = self.time
        self.shader['size'] = self.image.size
        self.shader['color'] = self.colour

        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render

class Rainbow(StaticEntity):#rainbow
    def __init__(self, pos, game_objects, size, parallax, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.parallax = parallax

    def release_texture(self):
        self.image.release()

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['rainbow'])#shader render

class Nebula(StaticEntity):#can be used as soul
    def __init__(self, pos, game_objects, size, parallax):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.parallax = parallax
        self.size = size
        self.time = 0

    def update(self, dt):
        self.time += dt * 0.1

    def draw(self, target):
        self.game_objects.shaders['nebula']['time'] = self.time
        self.game_objects.shaders['nebula']['resolution'] = self.size

        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['nebula'])#shader render

