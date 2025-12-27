import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Button():
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/button/', game_objects)        
        self.image = self.sprites['idle'][0]
                
        self.text = kwarg.get('text', '')

        position = kwarg.get('position', (0,0))
        self.rect = pygame.Rect(position, [self.image.width, self.image.height])
        self._calculate_text_position()

    def _calculate_text_position(self):# Use the underlying pygame font to measure the text        
        font_atlas = self.game_objects.font.font_atals
        text_width, text_height = font_atlas.font.size(self.text)                
        self.position = [self.rect.centerx - text_width // 2, self.rect.centery - text_height // 2]# Center the text in the button

    def hoover(self):
        pass

    def pressed(self):
        pass

    def render(self, target):
        self.game_objects.game.display.render(self.image, target, position = self.rect.topleft)   #render button
        self.game_objects.game.display.render_text(self.game_objects.font.font_atals, target, self.text, letter_frame = 1000, color = (255,255,255,255), position = self.position)