import pygame
from engine.utils import read_files
from gameplay.entities.base.static_entity import StaticEntity

class WaterReflection(StaticEntity):#water, e.g. village
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