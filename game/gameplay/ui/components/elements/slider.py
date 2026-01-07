import pygame
from engine.utils import read_files

class Slider():
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/slider/', game_objects)        
        self.bar = self.sprites['bar'][0]
        self.point = self.sprites['point'][0]
                
        position = kwarg.get('position', (0,0))
        self.rect = pygame.Rect(position, [self.bar.width, self.bar.height])
        
        # Volume value (0-100) - will be set from outside
        self.volume = 10
            
    def on_enter(self):
        'First time selected - start glow, play sound, etc.'
        pass
    
    def active(self):
        pass
    
    def on_exit(self):
        'Leaving button'
        pass
    
    def pressed(self):        
        pass
    
    def set_volume(self, volume):
        """Set the volume value (0-10)"""
        self.volume = max(0, min(10, volume))
    
    def get_point_position(self):
        """Calculate the position of the slider point based on volume"""
        # Calculate how far along the bar the point should be (0.0 to 1.0)
        volume_ratio = self.volume / 10.0
        
        # Calculate the x position (accounting for point width so it doesn't overflow)
        usable_width = self.bar.width - self.point.width
        point_x = self.rect.x + (usable_width * volume_ratio)
        
        # Center the point vertically on the bar
        point_y = self.rect.y + (self.bar.height - self.point.height) / 2
        
        return (point_x, point_y)

    def render(self, target):       
        # Render the background bar
        self.game_objects.game.display.render(self.bar, target, position=self.rect.topleft)
               
        # Render the point at the correct position
        point_pos = self.get_point_position()
        self.game_objects.game.display.render(self.point, target, position=point_pos)