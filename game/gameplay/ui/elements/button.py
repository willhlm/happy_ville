import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Button():
    def __init__(self, game_objects, **kwarg):
        self.position = kwarg.get('position', (0,0))
        self.image = kwarg.get('image', None)
        self.rect = pygame.Rect(self.position, [self.image.width, self.image.height])
        if kwarg.get('center', None):
            self.rect.center = self.position

    def hoover(self):
        pass

    def pressed(self):
        pass

#controllers
