import pygame

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.interactables.jet_burst.jet_burst_launch_area import JetBurstLaunchArea


class JetBurst(Interactables):
    """A hit-activated vent that launches overlapping movable entities."""

    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/jet_burst/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.launch_speed = abs(float(kwargs.get('launch_speed', 15)))
        self.active_duration = float(kwargs.get('active_duration', 8))
        power_source = kwargs.get('power_source', 'golden_fields_windmills')
        self.power_source = str(power_source).strip() if power_source else None
        self.relay_angle = int(kwargs.get('relay_angle', 90)) % 360

        self.hit_component.set_invincibility_time(self.active_duration)
        self.dir = [0, 1]

    def take_dmg(self, effect):
        self.activate()
        return effect

    def activate(self):
        if not self.functional:
            return False
        launch_area = JetBurstLaunchArea(
            self.hitbox,
            self.game_objects,
            source=self,
            launch_speed=self.launch_speed,
            duration=self.active_duration,
        )
        self.game_objects.entity_overlaps.add(launch_area)
        return True

    @property
    def functional(self):
        return self.game_objects.world_controller.power.is_powered(
            self.power_source,
            relay_angle=self.relay_angle,
        )
