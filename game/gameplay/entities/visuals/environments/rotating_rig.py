"""Visual rig that drives generated blade platforms."""

import pygame

from gameplay.entities.platforms.texture.rotating_blade import (
    RotatingBlade,
)
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects
from gameplay.world.configs.golden_fields_systems import rotating_rig_profile

class RotatingRig(LayeredObjects):
    """A layered environment visual that owns rotating blade platforms.

    Tiled property power_source (default golden_fields_windmills) selects its
    windmill network or water relay. relay_angle qualifies relay output only.
    Radius, blade_count, and rotation_phase configure its geometry and pose.
    """

    animations = {}

    def __init__(self, pos, game_objects, parallax, layer_name, **props):
        super().__init__(pos, game_objects, parallax, layer_name)
        self.power_source = str(props.get("power_source", "golden_fields_windmills")).strip()
        self.relay_angle = int(props.get("relay_angle", 90)) % 360
        self.init_sprites("assets/sprites/entities/visuals/environments/blade_rig/")
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos, (self.image.width, self.image.height))
        self.true_pos = list(self.rect.topleft)

        self.radius = float(props.get("radius", self.image.width * 0.5))
        self.blade_count = max(1, int(props.get("blade_count", 4)))
        self.angle = float(props.get("rotation_phase", 0.0)) % 360.0
        self.prev_angle = self.angle

        powered = self.game_objects.world_controller.power.is_powered(
            self.power_source,
            relay_angle=self.relay_angle,
        )
        profile = rotating_rig_profile(
            "golden_fields_default",
            powered,
        )
        self.rotation_speed = float(profile["rotation_speed"])
        self.turning = self.rotation_speed != 0

        self.blades = [RotatingBlade(self, index) for index in range(self.blade_count)]
        self._position_blades(self.angle)
        for blade in self.blades:
            blade.sync_pose()
        self.game_objects.platforms.add(*self.blades)

    def update(self, dt):
        self.prev_angle = self.angle
        if not self.turning:
            return
        self.angle = (self.angle + self.rotation_speed * dt) % 360.0
        self._position_blades(self.angle)

    def draw(self, target):
        alpha = self.game_objects.game.game_loop.alpha
        angle_delta = (self.angle - self.prev_angle + 180.0) % 360.0 - 180.0
        draw_angle = (self.prev_angle + angle_delta * alpha) % 360.0
        self.game_objects.game.display.render(
            self.image,
            target,
            position=(
                int(self.rect.left - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),
                int(self.rect.top - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]),
            ),
            angle=draw_angle,
        )

    def kill(self):
        for blade in self.blades:
            blade.kill()
        super().kill()

    def _position_blades(self, angle):
        for blade in self.blades:
            blade.follow_rig(angle)
