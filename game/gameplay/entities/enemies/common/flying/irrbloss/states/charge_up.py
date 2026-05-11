import math

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class ChargeUp(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('idle', 0.2)
        self.time = self.entity.config['attack']['charge_up_time']
        self.torpedo_speed = self.entity.config['speeds']['torpedo']

        dx, dy = self.player_distance
        distance = max(1, math.hypot(dx, dy))
        self.entity.torpedo_velocity = [
            (dx / distance) * self.torpedo_speed,
            (dy / distance) * self.torpedo_speed,
        ]
        self.entity.dir[0] = sign(dx)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
        self.time -= dt
        if self.time <= 0:
            self.enter_state('torpedo')
        
