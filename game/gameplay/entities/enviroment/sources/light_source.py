import pygame
from gameplay.entities.enviroment.base.layered_objects import LayeredObjects

class LightSource(LayeredObjects):#should we decrease alpha for large parallax?
    def __init__(self, pos, game_objects, parallax,layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name,live_blur)
        self.rect = pygame.Rect(pos[0],pos[1],16,16)
        self.true_pos = list(self.rect.topleft)
        self.hitbox = self.rect.copy()

    def update(self, dt):
        self.group_distance()

    def draw(self, target):
        pass