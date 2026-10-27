import pygame


class PlayerMapMarker:
    """Non-selectable overlay showing the player on the detailed local map."""

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.world_center = [0.0, 0.0]
        self.scroll = [0.0, 0.0]
        self.visible = False

        # Placeholder art until the final map marker sprite exists.
        surface = pygame.Surface((11, 11), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.polygon(surface, (30, 25, 20, 255), [(5, 0), (10, 5), (5, 10), (0, 5)])
        pygame.draw.polygon(surface, (255, 224, 105, 255), [(5, 2), (8, 5), (5, 8), (2, 5)])
        self.image = game_objects.game.display.surface_to_texture(surface)
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)

    def set_world_center(self, position):
        self.world_center = [float(position[0]), float(position[1])]
        self.visible = True
        self._sync_rect()

    def hide(self):
        self.visible = False

    def update_scroll(self, scroll):
        self.scroll = [float(scroll[0]), float(scroll[1])]
        self._sync_rect()

    def _sync_rect(self):
        self.rect.center = (
            round(self.world_center[0] + self.scroll[0]),
            round(self.world_center[1] + self.scroll[1]),
        )

    def draw(self, target):
        if self.visible:
            self.game_objects.game.display.render(
                self.image,
                target,
                position=self.rect.topleft,
            )

    def get_world_center(self):
        return tuple(self.world_center)
