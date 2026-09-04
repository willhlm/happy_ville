import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Text():
    def __init__(self, game_objects, text, position, size, font_style='text'):
        self.game_objects = game_objects
        self.text = text
        self.rect = pygame.Rect(position, [size[0], size[1]])     
        self.base_position = list(position)
        self.position = list(position)
        self.colour = [255,255,255,255]
        self.font_style = font_style
    
    def render(self, target):  
        self.game_objects.font.render(
            target,
            self.text,
            letter_frame=None,
            color=self.colour,
            position=self.position,
            width=self.rect[2],
            style=self.font_style,
        )

    def on_enter(self):
        pass

    def active(self):
        pass

    def on_exit(self):
        pass

    def update_scroll(self, scroll):
        """Position this text relative to a scrolling map background."""
        self.position = [
            self.base_position[0] + scroll[0],
            self.base_position[1] + scroll[1],
        ]
        self.rect.topleft = self.position
