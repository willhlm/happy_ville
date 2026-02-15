import pygame, random
from .base_tree import BaseTree
from engine.utils import read_files

class GeneralTree(BaseTree):
    animations = {}
    def __init__(self, pos, game_objects, parallax, layer_name, name, live_blur = False):        
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)                
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/environments/trees/' + name, game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        
        self.empty = game_objects.game.display.make_layer(self.image.size)
        self.noise_layer = game_objects.game.display.make_layer(self.image.size)

        self.time = random.randint(0, 100)
        
        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()

    def update(self, dt):
        self.time += dt 

    def draw(self, target):
        shader = self.game_objects.shaders['wind_foliage']
        shader['time'] = self.time * 0.1

        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.image.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.001
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0],self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [4,4]
        self.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        #shader['noise_texture'] = self.noise_layer.texture


        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))               
        self.game_objects.game.display.render(self.image, target, position = pos, shader = shader)#shader render      
