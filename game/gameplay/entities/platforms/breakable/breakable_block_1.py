import pygame
from engine.utils import read_files
from .base_breakable import BaseBreakable

class BreakableBlock_1(BaseBreakable):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/breakable/nordveden/type1/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
