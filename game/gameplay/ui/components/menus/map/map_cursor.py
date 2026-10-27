import math

import pygame


class MapCursor:
    """Animated selection marks around the currently focused map marker."""

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.target = None
        self.time = 0

        surface = pygame.Surface((7, 7), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.polygon(
            surface,
            (49, 31, 19, 255),
            ((3, 0), (6, 3), (3, 6), (0, 3)),
        )
        pygame.draw.polygon(
            surface,
            (255, 224, 104, 255),
            ((3, 1), (5, 3), (3, 5), (1, 3)),
        )
        self.image = game_objects.game.display.surface_to_texture(surface)

    def select(self, target):
        self.target = target
        self.time = 0

    def update(self, dt):
        self.time += dt * 0.12

    def draw(self, target):
        if self.target is None:
            return

        rect = self.target.rect
        width = self.image.width
        height = self.image.height
        gap = 4 + round(2 * (1 + math.sin(self.time)) * 0.5)
        positions = (
            (rect.left - gap - width, rect.centery - height * 0.5),
            (rect.right + gap, rect.centery - height * 0.5),
            (rect.centerx - width * 0.5, rect.top - gap - height),
            (rect.centerx - width * 0.5, rect.bottom + gap),
        )
        for position in positions:
            self.game_objects.game.display.render(
                self.image,
                target,
                position=position,
            )
