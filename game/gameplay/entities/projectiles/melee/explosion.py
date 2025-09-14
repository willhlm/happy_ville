import pygame
from gameplay.entities.projectiles.base.melee import Melee
from engine.utils import read_files

class Explosion(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = Explosion.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(entity.rect.centerx,entity.rect.centery,self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.dir = [0, 0]
        self.lifetime = 100
        self.dmg = 1

    def pool(game_objects):
        Explosion.sprites = read_files.load_sprites_dict('assets/sprites/attack/explosion/', game_objects)

    def reset_timer(self):
        self.kill()
