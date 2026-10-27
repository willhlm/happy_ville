import pygame


class MapPin:
    """Selectable map pin whose visibility is controlled by map progression."""

    def __init__(self, pos, game_objects, sprite_path):
        self.game_objects = game_objects
        surface = pygame.image.load(sprite_path).convert_alpha()
        self.image = game_objects.game.display.surface_to_texture(surface)
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.world_pos = [float(pos[0]), float(pos[1])]
        self.scroll = [0.0, 0.0]
        self.unlock_data = {}

    def update(self, dt):
        pass

    def reset(self):
        pass

    def update_scroll(self, scroll):
        self.scroll = [float(scroll[0]), float(scroll[1])]
        self._sync_rect()

    def set_world_center(self, position):
        self.world_pos = [
            float(position[0]) - self.image.width * 0.5,
            float(position[1]) - self.image.height * 0.5,
        ]
        self._sync_rect()

    def _sync_rect(self):
        self.rect.topleft = (
            round(self.world_pos[0] + self.scroll[0]),
            round(self.world_pos[1] + self.scroll[1]),
        )

    def draw(self, target):
        self.game_objects.game.display.render(
            self.image,
            target,
            position=self.rect.topleft,
        )

    def get_world_center(self):
        return (
            self.world_pos[0] + self.image.width * 0.5,
            self.world_pos[1] + self.image.height * 0.5,
        )
