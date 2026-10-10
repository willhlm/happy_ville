import pygame

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables


class Battery(Interactables):
    """Display the map-load charge of an authored windmill network."""

    DEFAULT_WIND_NETWORK = "golden_fields_windmills"
    STATES_BY_ACTIVE_COUNT = ("idle", "one_fill", "two_fill", "full")

    def __init__(self, pos, game_objects, **props):
        super().__init__(pos, game_objects)
        self.wind_network = str(
            props.get("wind_network", self.DEFAULT_WIND_NETWORK)
        ).strip()
        windmills = game_objects.world_controller.golden_fields.windmills
        self.active_windmills = windmills.active_count(self.wind_network)
        state_index = min(
            self.active_windmills,
            len(self.STATES_BY_ACTIVE_COUNT) - 1,
        )
        self.battery_state = self.STATES_BY_ACTIVE_COUNT[state_index]

        self.sprites = read_files.load_sprites_dict(
            "assets/sprites/entities/interactables/battery/", game_objects
        )
        self.image = self.sprites[self.battery_state][0]
        self.animation.play(self.battery_state)
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.hitbox.midbottom = self.rect.midbottom

        self.hit_component.set_invincibility(True)
