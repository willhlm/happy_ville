import pygame
from engine import constants as C
from engine.utils import read_files
from engine.system import animation
from gameplay.entities.platforms.components.surface_collision import (
    OneWayUpSurfaceCollisionComponent,
)
from gameplay.entities.platforms.texture.textured_platform import TexturedPlatform
from . import states_basic


class PowerPlant(TexturedPlatform):
    """A plant whose initial visual and collision state is power-driven.

    Power is sampled once during construction. Relay changes do not affect an
    already loaded room; the new state is picked up on the next map load.
    """

    def __init__(self, pos, game_objects, **props):
        super().__init__(pos, game_objects)
        power_source = props.get("power_source", "water_relay_1")
        self.power_source = str(power_source).strip() if power_source else None
        self.relay_angle = int(props.get("relay_angle", 270)) % 360
        self.powered = game_objects.world_controller.power.is_powered(self.power_source, relay_angle=self.relay_angle)

        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/platforms/power_plant/", game_objects)
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.surface_collision = OneWayUpSurfaceCollisionComponent(self)

        self.animation = animation.Animation(self)
        state_type = states_basic.Idle if self.powered else states_basic.Wither
        self.currentstate = state_type(self)
        self.bounce_velocity = abs(float(props.get("bounce_velocity", 6)))
        self.jump_boost = abs(self.bounce_velocity / C.jump_vel_player)

    def set_collision_enabled(self, enabled):
        self.hitbox = self.rect.copy()
        if not enabled:
            self.hitbox.size = (0, 0)

    def on_platform_collision(self, entity, side, axis, collision_kind="block"):
        if axis != "y" or side != "bottom":
            return

        self.currentstate.handle_input("land")
        entity.velocity[1] -= self.bounce_velocity

        if entity is not self.game_objects.player:
            return

        entity.currentstate.enter_state("jump", air_timer=0)
        entity.arm_bounce_jump(jump_boost=self.jump_boost)

    def get_wall_samples(self, entity):
        return ()

    def get_ceiling_samples(self, entity):
        return ()
