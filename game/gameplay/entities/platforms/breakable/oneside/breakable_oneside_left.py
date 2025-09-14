import pygame
from engine.utils import read_files
from .base_breakable_oneside import BaseBreakableOneside

class BreakableOnesideLeft(BaseBreakableOneside):
    def __init__(self, pos, game_objects, ID, path):
        super().__init__(pos, game_objects, ID)
        self.sprites = read_files.load_sprites_dict(path, game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

    def take_dmg(self, projectile):
        if self.hitbox.centerx - projectile.rect.centerx > 0:#projectile from left: depends on the speciic objects
            super().take_dmg(projectile)            

#dynamics (moving) ones
