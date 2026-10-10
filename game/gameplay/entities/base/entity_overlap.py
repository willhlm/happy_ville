import pygame

from gameplay.entities.base.static_entity import StaticEntity


class EntityOverlap(StaticEntity):
    """Invisible overlap volume evaluated against dynamic world entities."""

    def __init__(self, rect, game_objects):
        super().__init__(rect.topleft, game_objects)
        self.rect = pygame.Rect(rect)
        self.hitbox = self.rect.copy()
        self.true_pos = list(self.rect.topleft)

    def on_collision(self, entity):
        pass

    def collision(self, entity):
        pass

    def on_noncollision(self, entity):
        pass

    def on_kill_cleanup(self):
        self.game_objects.physics.overlap_dispatcher.forget_target(self)
        super().on_kill_cleanup()
