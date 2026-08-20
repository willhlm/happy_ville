"""Collision platform used by Golden Fields rotating rigs."""

import math

from engine.utils import read_files
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform


class GoldenfieldsRotatingBlade(DynamicPlatform):
    """A fixed-size platform whose centre orbits a visual rig."""

    def __init__(self, rig, index):
        self.game_objects = rig.game_objects
        self.sprites = read_files.load_sprites_dict(
            "assets/sprites/entities/platforms/rotating_blades/", self.game_objects
        )
        self.image = self.sprites["idle"][0]
        super().__init__(
            (0, 0),
            self.game_objects,
            size=(self.image.width, self.image.height),
        )
        self.rig = rig
        self.index = index
        self.prev_true_pos = self.true_pos.copy()
        # A blade is a moving support, not a crushing trap.  Its displacement
        # is passed to supported entities through ``get_support_motion``.
        self.crushes_entities = False

    def update(self, dt):
        self.follow_rig(self.rig.angle)

    def draw(self, target):
        alpha = self.game_objects.game.game_loop.alpha
        interp_x = self.prev_true_pos[0] + (self.true_pos[0] - self.prev_true_pos[0]) * alpha
        interp_y = self.prev_true_pos[1] + (self.true_pos[1] - self.prev_true_pos[1]) * alpha
        self.game_objects.game.display.render(
            self.image,
            target,
            position=(
                int(interp_x - self.game_objects.camera_manager.camera.interp_scroll[0]),
                int(interp_y - self.game_objects.camera_manager.camera.interp_scroll[1]),
            ),
        )

    def release_texture(self):
        for state in self.sprites.values():
            for frame in state:
                frame.release()

    def follow_rig(self, angle):        
        angle = math.radians(
            angle + self.index * 360.0 / self.rig.blade_count
        )
        hub_x, hub_y = self.rig.rect.center
        orbit_radius = self.rig.radius * 0.5
        self.old_hitbox = self.hitbox.copy()
        previous_position = self.rect.topleft
        self.prev_true_pos = self.true_pos.copy()
        self.rect.center = (
            round(hub_x + math.cos(angle) * orbit_radius),
            round(hub_y + math.sin(angle) * orbit_radius),
        )
        self.update_hitbox()
        self.true_pos = list(self.rect.topleft)
        self.delta = [
            self.rect.left - previous_position[0],
            self.rect.top - previous_position[1],
        ]

    def sync_pose(self):
        """Set an initial pose without an artificial first-frame movement."""
        self.old_hitbox = self.hitbox.copy()
        self.prev_true_pos = self.true_pos.copy()
        self.delta = [0, 0]

    def get_support_motion(self, entity):
        """Carry a supported entity by this blade's exact frame displacement."""
        return self.delta if self.rig.turning else None
