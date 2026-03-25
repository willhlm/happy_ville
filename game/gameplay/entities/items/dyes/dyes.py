import pygame
from engine.utils import read_files
from gameplay.entities.items.base.interactable_item import InteractableItem
from .config import DYES, ORIGINAL_COLOUR

class Dyes(InteractableItem):#ring in which to attach radnas
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.name = kwarg['name']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/dyes/' + self.name + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.currentstate.enter_state('Idle')

        self.type = DYES[self.name]['type']
        self.repalce_colour = DYES[self.name][self.type]['colours']
        self.target_colour = ORIGINAL_COLOUR[self.type]

    def pickup(self, player):
        super().pickup(player)
        player.backpack.inventory.add_dye(self, name = self.name)
