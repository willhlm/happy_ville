import pygame
from gameplay.entities.visuals.enviroment.base.layered_objects import LayeredObjects

class LjusMaskar(LayeredObjects):
    animations = {}
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.init_sprites('assets/sprites/entities/visuals/enviroment/ljusmaskar/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft