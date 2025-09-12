import pygame 
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Crystal_source(Interactables):#the thng that spits out crystals in crystal mines
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/crystal_source/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.time = 0
        self.frequency = kwarg.get('frequency', 15)
        self.kwarg = kwarg

    def group_distance(self):
        pass

    def update(self, dt):
        super().update(dt)
        self.time += dt
        if self.time > self.frequency:
            crystal = Projectile_1(self.rect.center, self.game_objects, **self.kwarg)
            self.game_objects.eprojectiles.add(crystal)
            self.time = 0