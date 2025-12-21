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
        self.max_blur = 10.0
        self.smoothing_speed = 0.05
        
        # State tracking
        self.is_colliding = False  #Track collision state
        self.interacted = False
        self.blur_timer = 0

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
        self.is_colliding = True  #Set state
        
        # Increment timer while colliding
        if self.blur_timer < C.fps:
            self.blur_timer += 1
            self.game_objects.camera_manager.zoom(rate=self.rate,scale=self.scale,center=self.center)
    
    def on_collision(self, entity):
        """Called ONCE when entity enters"""
        # Trigger zoom only once on entry
        if not self.interacted:
            self.interacted = True
            # Don't zoom immediately - wait for timer
    
    def on_noncollision(self, entity):
        """Called ONCE when entity exits"""
        self.is_colliding = False  #Clear state
        
        # Trigger zoom out only once on exit
        if self.interacted:
            self.interacted = False
            self.blur_timer = 0  # Reset timer
            self.game_objects.camera_manager.zoom_out(rate=self.rate * 2)
    
    def update_blur(self):
        """
        Smoothly update blur radius on all active screens.
        Called every frame from update().
        """
        # Check if we should zoom (after timer delay)
        if self.is_colliding and self.blur_timer >= C.fps and not self.interacted:
            # Timer finished - trigger zoom
            self.interacted = True
            self.game_objects.camera_manager.zoom(rate=self.rate, scale=self.scale, center=self.center)
        
        # Update blur for all screens
        for screen in self.game_objects.game.screen_manager.active_screens:
            screen_obj = self.game_objects.game.screen_manager.screens[screen]
            blur_shader = screen_obj.post_process.shaders['Blur']
            current_blur = blur_shader.radius
            current_parallax = screen_obj.parallax

            # Calculate target blur based on collision state
            if self.is_colliding and self.blur_timer >= C.fps:
                # Colliding and timer done - distance-based blur
                parallax_diff = abs(current_parallax[0] - self.target_parallax[0])
                normalized_diff = min(parallax_diff / 1.0, 1.0)
                target_blur = self.min_blur + normalized_diff * (self.max_blur - self.min_blur)
            else:
                # Not colliding or timer not done - default blur
                target_blur = 0.01 if current_parallax[0] == 1 else functions.blur_radius(current_parallax)

            # Smooth interpolation (happens every frame)
            new_blur = current_blur + (target_blur - current_blur) * self.smoothing_speed
            blur_shader.set_radius(new_blur)