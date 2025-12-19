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
        self.target_parallax = kwarg.get('target_parallax', (0.2, 0.2))  # Desired parallax
        self.blur_timer = C.fps

        # Blur configuration
        self.min_blur = 0.01   # Blur when parallax is very close to target
        self.max_blur = 10.0  # Blur when parallax is very far from target
        self.smoothing_speed = 0.05  # Controls how fast blur interpolates
        self.interacted = False

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.group_distance()

    def collision(self, entity):
        self.blur_timer -= 1
        if self.blur_timer < 0:#make a delay in the blur and zoom
            self.update_blur(collision=True)
        
            if self.interacted: return# Trigger zoom only once per collision start
            self.interacted = True
            self.game_objects.camera_manager.zoom(rate=self.rate,scale=self.scale,center=self.center)

    def noncollision(self, entity):        
        self.update_blur(collision=False)
        
        if not self.interacted: return# Trigger zoom out only once per collision end
        self.interacted = False
        self.blur_timer = C.fps#reset the value for plaer_collision
        self.game_objects.camera_manager.zoom_out(rate = self.rate * 2)

    def update_blur(self, collision: bool):
        """Smoothly update blur radius on all active screens."""
        for screen in self.game_objects.game.screen_manager.active_screens:
            screen_obj = self.game_objects.game.screen_manager.screens[screen]
            blur_shader = screen_obj.post_process.shaders['Blur']
            blur_radius = blur_shader.radius
            current_parallax = screen_obj.parallax

            if collision:# Distance-based blur: further from target → more blur                
                parallax_diff = abs(current_parallax[0] - self.target_parallax[0])
                normalized_diff = min(parallax_diff / 1.0, 1.0)
                target_blur = self.min_blur + normalized_diff * (self.max_blur - self.min_blur)
            else:# Revert to default: sharp if parallax = 1                
                target_blur = 0.01 if current_parallax[0] == 1 else functions.blur_radius(current_parallax)

            # Smooth interpolation
            blur_radius += (target_blur - blur_radius) * self.smoothing_speed

            blur_shader.set_radius(blur_radius)    




