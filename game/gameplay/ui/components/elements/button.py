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
        self.colour = [255,255,255,255]
        
        # Animation properties
        self.scale_x = 1.0
        self.target_scale_x = 1.0
        self.scale_speed = 0.15  # How fast it returns to normal

    def _calculate_text_position(self):
        font_atlas = self.game_objects.font.font_atals
        text_width, text_height = font_atlas.font.size(self.text)                
        self.position = [self.rect.centerx - text_width // 2, self.rect.centery - text_height // 2]

    def on_enter(self):
        'First time selected - start glow, play sound, etc.'
        self.colour = [255, 255, 0, 255]
        self.target_scale_x = 1.1  # Stretch to 115% width
    
    def active(self):
        # Smooth scale back to normal
        self.scale_x += (self.target_scale_x - self.scale_x) * self.scale_speed
        
        # Once close to target, snap to 1.0
        if abs(self.scale_x - 1.0) < 0.01 and self.target_scale_x == 1.0:
            self.scale_x = 1.0
    
    def on_exit(self):
        'Leaving button - fade out glow, reset state, etc.'
        self.colour = [255, 255, 255, 255]
        self.target_scale_x = 1.0
        self.scale_x = 1.0
    
    def pressed(self):
        # Button was activated
        pass

    def render(self, target):
        # Calculate centered position accounting for horizontal stretch
        # When scale_x = 1.15, button is 15% wider, so shift left by 7.5% of original width
        offset_x = self.rect.width * (self.scale_x - 1.0) * 0.5
        render_pos = (self.rect.left - offset_x, self.rect.top)
        
        self.game_objects.game.display.render(self.image, target, position=render_pos,scale=(self.scale_x, 1.0))
        
        # Text stays in original position (doesn't stretch)
        self.game_objects.game.display.render_text(self.game_objects.font.font_atals, target, self.text, letter_frame=1000, color=self.colour, position=self.position)