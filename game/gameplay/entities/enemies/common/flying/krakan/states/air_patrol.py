from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

from .common import player_in_range


class AirPatrol(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.patrol = entity.config['patrol']
        self.home_radius = self.patrol['home_radius']
        self.ground_speed = self.patrol['ground_speed']
        self.fall_speed = entity.config['speeds']['fall']
        self.fall_max = entity.config['speeds']['fall_max']
        self.ground_grace_time = self.patrol['grounded_grace_time']
        self.grounded_timer = self.ground_grace_time
        self.entity.animation.play('fly', 0.18)

    def update_logic(self, dt):
        if player_in_range(self, self.aggro_distance):
            self.enter_state('chase')
            return

        if self.entity.is_on_floor():
            self.grounded_timer -= dt
            if self.grounded_timer <= 0:
                self.enter_state('patrol')
                return
        else:
            self.grounded_timer = self.ground_grace_time

        drift = self.entity.original_pos[0] - self.entity.hitbox.centerx
        self.entity.velocity[0] += dt * sign(drift) * self.ground_speed * 0.35
        self.entity.velocity[1] = min(self.entity.velocity[1] + dt * self.fall_speed, self.fall_max)
