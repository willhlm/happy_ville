import pygame, random
from gameplay.entities.base.static_entity import StaticEntity
from gameplay.entities.projectiles import FallingRock

class AreaSpawner(StaticEntity):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.game_objects = game_objects        
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()

        self.game_objects.signals.subscribe('fall_projectiles', self.spawn_falling_projectiles)
            
    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def spawn_falling_projectiles(self, count=10):
        for i in range(count):

            half_width = self.rect.width * 0.5
            half_height = self.rect.height * 0.5
            position = [self.rect.centerx + random.randint(-half_width, half_width), self.rect.centery + random.randint(-half_height, half_height)]

            self.game_objects.eprojectiles.add(FallingRock(position, self.game_objects))
