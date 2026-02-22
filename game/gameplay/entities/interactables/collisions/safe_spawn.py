import pygame 
from .base_collisions import BaseCollisions

class SafeSpawn(BaseCollisions):#area which gives the coordinates which will make aila respawn at after falling into a hole
    def __init__(self, pos, game_objects, size, position):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.position = position

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def collision(self, entity):
        entity.backpack.map.save_safespawn(self.position)

