import pygame
from engine.utils import read_files
from .controllers import Controllers

class Xbox(Controllers):
    def __init__(self, pos, game_objects,type):
        super().__init__(pos, game_objects,type)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/controller/xbox/',game_objects)
        self.image = self.sprites['a_idle'][0]
        self.animation.play('a_idle')
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

