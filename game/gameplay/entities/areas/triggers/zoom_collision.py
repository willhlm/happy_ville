import pygame

from engine.utils import functions

from ..base import BaseArea


class ZoomCollision(BaseArea):
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
        self.update_blur()

    def collision(self, entity):
        if self.blur_timer < 60:
            self.blur_timer += 1
        else:
            if not self.zoomed:
                self.zoomed = True
                self.game_objects.camera_manager.zoom(rate=self.rate,scale=self.scale,center=self.center)

    def on_noncollision(self, entity):
        self.blur_timer = 0
        self.zoomed = False
        self.game_objects.camera_manager.zoom_out(rate=self.rate * 2)

    def update_blur(self):
        for screen in self.game_objects.game.screen_manager.active_screens:
            screen_obj = self.game_objects.game.screen_manager.screens[screen]
            blur_shader = screen_obj.post_process.shaders['Blur_fast']
            current_blur = blur_shader.radius
            current_parallax = screen_obj.parallax

            if self.zoomed:
                target_blur = functions.blur_radius(current_parallax,  target_parallax = self.target_parallax[0], min_blur=self.min_blur, max_blur=self.max_blur)
            else:
                target_blur = functions.blur_radius(current_parallax,  target_parallax = 1, min_blur=self.min_blur, max_blur=self.max_blur)

            new_blur = current_blur + (target_blur - current_blur) * self.smoothing_speed
            blur_shader.set_radius(new_blur)
