import pygame

from ..base import BaseArea


class WorldTextTrigger(BaseArea):
    """An invisible map area that displays text while the player overlaps it."""

    def __init__(self, pos, game_objects, size, **kwargs):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()

        self.text = str(kwargs.get("text", ""))
        self.width = int(kwargs.get("width", max(self.rect.width, 80)))
        self.offset_x = int(kwargs.get("offset_x", -self.width))
        self.offset_y = int(kwargs.get("offset_y", 0))
        self.fade_speed = float(kwargs.get("fade_speed", 8))
        self.visible = False
        self.alpha = self.game_objects.fade.create("alpha", 0)
        self.non_collision = bool(kwargs.get("non_col", False))
        self.kill_con = str(kwargs.get("kill_con", ""))
        self.kill_flag = False

    def on_collision(self, entity):
        self.visible = True

    def on_noncollision(self, entity):
        self.visible = self.non_collision

    def update(self, dt):
        if self.kill_con == 'drop_down':
            if self.game_objects.player.go_through['drop_through']:
                self.visible = False
                self.non_collision = False
                self.kill_flag = True
        direction = 1 if self.visible else -1
        self.alpha.step(dt * self.fade_speed * direction)
        if self.kill_flag and self.alpha.value <= 0:
            self.kill()

    def draw(self, target):
        if not self.text or self.alpha.value <= 0:
            return

        camera_scroll = self.game_objects.camera_manager.camera.scroll
        position = (
            int(self.rect.centerx - camera_scroll[0] + self.offset_x),
            int(self.rect.top - camera_scroll[1] + self.offset_y),
        )
        self.game_objects.font.render(
            target,
            self.text,
            position=position,
            width=self.width,
            alignment="center",
            color=(255, 255, 255, int(self.alpha.value)),
        )
