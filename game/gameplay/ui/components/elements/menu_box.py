import pygame
from engine.utils import read_files

class MenuBox():
    def __init__(self, game_objects):
        img = pygame.image.load("assets/sprites/ui/elements/box.png").convert_alpha()#select box
        self.image = game_objects.game.display.surface_to_texture(img)
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)

    def update(self,pos):
        pass

    def draw(self,screen):
        pass

