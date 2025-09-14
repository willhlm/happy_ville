import pygame
from engine.utils import read_files
from gameplay.entities.items.base.interactable_item import InteractableItem

class Tungsten(InteractableItem):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Tungsten.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.description = 'A heavy rock'

    def pickup(self, player):
        super().pickup(player)
        player.backpack.inventory.add(self)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/tungsten/',game_objects)
        super().pool(game_objects)