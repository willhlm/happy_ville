import pygame
from engine.utils import read_files
from gameplay.entities.items.base.interactable_item import InteractableItem
from .config import DYES, PALETTE_CHANNELS

class Dyes(InteractableItem):#ring in which to attach radnas
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.name = kwarg['name']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/dyes/' + self.name + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        dye_config = DYES[self.name]
        self.channel = dye_config['channel']
        self.target_colour = PALETTE_CHANNELS[self.channel]['source']
        self.replace_colour = dye_config['target']

    def pickup(self, player):
        super().pickup(player)
        player.backpack.inventory.add_dye(self, name = self.name)
