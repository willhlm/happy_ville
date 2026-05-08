import random
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Spawn(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("spawn", 0.2)

    def update_logic(self, dt):
        pass

    def increase_phase(self):
        self.enter_state("patrol")    
