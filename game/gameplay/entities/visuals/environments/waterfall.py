from engine.utils import read_files
from gameplay.entities.base.static_entity import StaticEntity

class Waterfall(StaticEntity):
    def __init__(self, pos, game_objects, parallax, size, layer_name):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.layer_name = layer_name

        self.size = size
        self.rect[2], self.rect[3] = size[0], size[1]   

        self.empty = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)
        self.blur_layer = game_objects.game.display.make_layer(size)
        self.time = 5*100#offset the time

        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/environments/waterfall/')

        px, py = self.parallax
        p_factor = 0.5 * (px + py)
        self.spatial_emitter_id = game_objects.sound.register_spatial_rect(
            sound=sounds['idle'][0],
            get_rect=lambda: self.rect,       
            base_volume=1 * p_factor,
            loops=-1,
            min_dist=96 * p_factor,
            max_dist=700 * p_factor,
            listener_transform=lambda p: (
                p[0] - px * self.game_objects.camera_manager.camera.interp_scroll[0],
                p[1] - py * self.game_objects.camera_manager.camera.interp_scroll[1],
            ),
        )

    def release_texture(self):
        self.empty.release()
        self.noise_layer.release()
        self.blur_layer.release()
        self.game_objects.sound.unregister_emitter(self.spatial_emitter_id)

    def update(self, dt):
        self.time += dt * 0.01

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

        blit_pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.shaders['waterfall']['section'] = [blit_pos[0],blit_pos[1],self.size[0],self.size[1]]

        if self.parallax[0] == 1:#TODO, blue state #don't blur if there is no parallax
            self.game_objects.game.display.render(self.empty.texture, target, position = blit_pos, shader = self.game_objects.shaders['waterfall'])
        else:
            self.blur_layer.clear(0, 0, 0, 0)
            self.game_objects.shaders['blur']['blurRadius'] = 1/self.parallax[0]#set the blur redius
            self.game_objects.game.display.render(self.empty.texture, self.blur_layer, shader = self.game_objects.shaders['waterfall'])
            self.game_objects.game.display.render(self.blur_layer.texture, target, position = blit_pos, shader = self.game_objects.shaders['blur'])
