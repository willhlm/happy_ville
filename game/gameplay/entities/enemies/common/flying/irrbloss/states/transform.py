import random

from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Transform(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('transform', 0.2)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
        
    def increase_phase(self):
        self.enter_state('charge_up')
