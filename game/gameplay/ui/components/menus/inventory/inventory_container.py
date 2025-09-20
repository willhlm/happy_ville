import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class InventoryContainer(AnimatedEntity):#for invenotry, will contain items
    def __init__(self, pos, game_objects, item):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/menus/inventory/container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.item = item

    def get_item(self):
        return self.item

