import pygame
from engine import constants as C
from gameplay.entities.interactables.base.interactables import Interactables
from engine.utils import functions

class ZoomCollision(Interactables):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()

        self.rate = kwarg.get('rate', 1)
        self.scale = kwarg.get('scale', 1)
        self.center = kwarg.get('center', (0.5, 0.5))
        self.target_parallax = kwarg.get('target_parallax', (0.2, 0.2))
        
        # Blur configuration
        self.min_blur = 0.01
        self.max_blur = 10
        self.smoothing_speed = 0.05
        
        # State tracking
        self.blur_timer = 0
        self.zoomed = False

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        """Called every frame - handle continuous blur updates here"""
        self.group_distance()        
        self.update_blur()#Always updating blur
    
    def collision(self, entity):
        """Called EVERY frame while colliding"""        
        # Increment timer while colliding
        if self.blur_timer < 60:
            self.blur_timer += 1                  
        else:
            if not self.zoomed: 
                self.zoomed = True  
                self.game_objects.camera_manager.zoom(rate=self.rate,scale=self.scale,center=self.center)
        
    def on_noncollision(self, entity):
        """Called ONCE when entity exits"""        
        # Trigger zoom out only once on exit
        self.blur_timer = 0  # Reset timer
        self.zoomed = False
        self.game_objects.camera_manager.zoom_out(rate=self.rate * 2)
    
    def update_blur(self):
        """
        Smoothly update blur radius on all active screens.
        Called every frame from update().
        """       
        # Update blur for all screens
        for screen in self.game_objects.game.screen_manager.active_screens:
            screen_obj = self.game_objects.game.screen_manager.screens[screen]
            blur_shader = screen_obj.post_process.shaders['Blur_fast']#assumes that there is a blur pp shader
            current_blur = blur_shader.radius
            current_parallax = screen_obj.parallax

            # Calculate target blur based on collision state
            if self.zoomed:
                # Colliding and timer done - distance-based blur
                target_blur = functions.blur_radius(current_parallax,  target_parallax = self.target_parallax[0], min_blur=self.min_blur, max_blur=self.max_blur)
            else:
                # Not colliding or timer not done - default blur
                target_blur = functions.blur_radius(current_parallax,  target_parallax = 1, min_blur=self.min_blur, max_blur=self.max_blur)

            # Smooth interpolation (happens every frame)
            new_blur = current_blur + (target_blur - current_blur) * self.smoothing_speed
            blur_shader.set_radius(new_blur)