from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Torpedo(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('torpedo', 0.2)
        self.time = self.entity.config['attack']['torpedo_time']

    def update_logic(self, dt):
        self.entity.velocity[0] = self.entity.torpedo_velocity[0]
        self.entity.velocity[1] = self.entity.torpedo_velocity[1]
        self.entity.dir[0] = sign(self.entity.torpedo_velocity[0])
        self.time -= dt
        if self.time <= 0:
            self.enter_state('charge_up')
