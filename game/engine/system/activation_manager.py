import pygame

class ActivationManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.activation_margin = (220, 140)
        self.camera_left = 0
        self.camera_top = 0
        self.camera_right = 0
        self.camera_bottom = 0

    def update(self):#called from game_objects
        camera = self.game_objects.camera_manager.camera
        window_w, window_h = self.game_objects.game.window_size
        self.camera_left = camera.scroll[0]
        self.camera_top = camera.scroll[1]
        self.camera_right = self.camera_left + window_w
        self.camera_bottom = self.camera_top + window_h

    def is_active(self, sprite):
        if getattr(sprite, "always_active", False):
            return True
        if not self._is_managed(sprite):
            return True
        rect = self._get_world_rect(sprite)
        if rect is None:
            return True

        margin_x, margin_y = self._get_margin(sprite)
        left, top, right, bottom = self._get_camera_bounds(sprite)

        return (
            rect.right >= left - margin_x
            and rect.left <= right + margin_x
            and rect.bottom >= top - margin_y
            and rect.top <= bottom + margin_y
        )

    def sleep(self, sprite):
        if not self._is_managed(sprite):
            return
        if sprite.pause_group in sprite.groups():
            return
        sprite.remove(sprite.group)
        sprite.add(sprite.pause_group)

    def wake(self, sprite):
        if not self._is_managed(sprite):
            return
        if sprite.group in sprite.groups():
            return
        sprite.add(sprite.group)
        sprite.remove(sprite.pause_group)

    def _is_managed(self, sprite):
        return hasattr(sprite, "group") and hasattr(sprite, "pause_group")

    def _get_camera_bounds(self, sprite):
        parallax = getattr(sprite, "parallax", None)

        if parallax is None:
            return self.camera_left, self.camera_top, self.camera_right, self.camera_bottom

        return (
            self.camera_left * parallax[0],
            self.camera_top * parallax[1],
            self.camera_right * parallax[0],
            self.camera_bottom * parallax[1],
        )

    def _get_world_rect(self, sprite):
        rect = getattr(sprite, "rect", None)
        if rect is not None:
            return rect

        hitbox = getattr(sprite, "hitbox", None)
        if hitbox is not None:
            return hitbox

        true_pos = getattr(sprite, "true_pos", None)
        if true_pos is None:
            return None

        return pygame.Rect(int(true_pos[0]), int(true_pos[1]), 1, 1)

    def _get_margin(self, sprite):
        margin = getattr(sprite, "activation_margin", None)
        if margin is None:
            margin = self.activation_margin

        if isinstance(margin, (int, float)):
            value = int(margin)
            return value, value
        return int(margin[0]), int(margin[1])
