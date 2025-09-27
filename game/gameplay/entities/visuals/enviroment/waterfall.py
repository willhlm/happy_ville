from engine.utils import read_files
from gameplay.entities.base.static_entity import StaticEntity

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

        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/enviroments/waterfall/')
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
            self.game_objects.game.display.render(self.empty.texture, target, position = blit_pos, shader = self.game_objects.shaders['waterfall'])
        else:
            self.blur_layer.clear(0, 0, 0, 0)
            self.game_objects.shaders['blur']['blurRadius'] = 1/self.parallax[0]#set the blur redius
            self.game_objects.game.display.render(self.empty.texture, self.blur_layer, shader = self.game_objects.shaders['waterfall'])
            self.game_objects.game.display.render(self.blur_layer.texture, target, position = blit_pos, shader = self.game_objects.shaders['blur'])