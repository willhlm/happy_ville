import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity
from . import states_health

class Spirit(AnimatedEntity):#gameplay UI
    def __init__(self,game_objects, path = 'assets/sprites/ui/gameplay/spirit/'):
        super().__init__([0,0],game_objects)
        self.sprites=read_files.load_sprites_dict(path, game_objects)
        self.image = self.sprites['death'][0]
        self.animation.play('death')
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.currentstate = states_health.Death(self)
        self.health = 0

