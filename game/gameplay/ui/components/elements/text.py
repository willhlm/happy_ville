import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Text():
    def __init__(self, game_objects, text, position):
        self.game_objects = game_objects
                
        text_width, text_height = self.game_objects.font.font_atals.font.size(text)     
        self.text = text
        self.rect = pygame.Rect(position, [text_width, text_height])     
        self.position = position
        self.colour = [255,255,255,255]   
    
    def render(self, target):     
        self.game_objects.game.display.render_text(self.game_objects.font.font_atals, target, self.text, letter_frame=1000, color=self.colour, position=self.position)

    def on_enter(self):
        pass

    def active(self):
        pass

    def on_exit(self):
        pass