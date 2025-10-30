import pygame
from engine.utils import read_files

class MovementHud():#gameplay UI
    def __init__(self,entity):
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/hud/ability/frame/',entity.game_objects)
        self.entity = entity
        self.game_objects = entity.game_objects#animation need it
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this

    def update(self, dt):
        pass

