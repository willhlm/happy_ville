"""Golden Fields visual rig that drives generated blade platforms."""

import pygame

from gameplay.entities.platforms.texture.goldenfields_rotating_blade import (
    GoldenfieldsRotatingBlade,
)
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects


class GoldenfieldRotatingRig(LayeredObjects):
    """A layered environment visual that owns rotating blade platforms."""

    animations = {}

    def __init__(self, pos, game_objects, parallax, layer_name, **props):
        super().__init__(pos, game_objects, parallax, layer_name)
        self.wind_network = str(props.get("wind_network", "golden_fields_liquid"))
        controller = game_objects.world_controller.golden_fields
        self.init_sprites("assets/sprites/entities/visuals/environments/blade_rig/")
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos, (self.image.width, self.image.height))
        self.true_pos = list(self.rect.topleft)

        self.radius = float(props.get("radius", self.image.width * 0.5))
        self.blade_count = max(1, int(props.get("blade_count", 4)))
        self.rotation_speed = float(props.get("rotation_speed", 2.5))
        self.angle = float(props.get("rotation_phase", 0.0)) % 360.0
        self.prev_angle = self.angle
        self.turning = controller.windmill_turning_count(self.wind_network) > 0
        self._subscribed = True

        self.blades = [
            GoldenfieldsRotatingBlade(self, index)
            for index in range(self.blade_count)
        ]
        self._position_blades(self.angle)
        for blade in self.blades:
            blade.sync_pose()
        self.game_objects.platforms.add(*self.blades)
        controller.subscribe_windmill_network(self.wind_network, self._on_network_changed)

    def update(self, dt):
        if not self.turning:
            return
        self.prev_angle = self.angle
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
        self._unsubscribe_network()
        for blade in self.blades:
            blade.kill()
        super().kill()

    def release_texture(self):
        self._unsubscribe_network()

    def _unsubscribe_network(self):
        if not self._subscribed:
            return
        self.game_objects.world_controller.golden_fields.unsubscribe_windmill_network(
            self.wind_network, self._on_network_changed
        )
        self._subscribed = False

    def _on_network_changed(self, *, turning_count, **kwargs):
        self.turning = turning_count > 0

    def _position_blades(self, angle):
        for blade in self.blades:
            blade.follow_rig(angle)
