import pygame
from .base_tree import BaseTree

class NordvedenTree_2(BaseTree):
    animations = {}
    def __init__(self, pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.init_sprites('assets/sprites/entities/visuals/environments/trees/nordveden/tree_2/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft

        #for leaves
        position = self.rect.center
        size = [64,64]
        self.spawn_box = [position,size]
        self.create_leaves()