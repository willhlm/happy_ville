from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Death(BaseState):
    def __init__(self, entity, deciders, config_key, **kwarg):
        super().__init__(entity, deciders, config_key)
        self.entity.killed()
        self.entity.dead()
        self.entity.animation.play('death', 0.2)

    @property
    def allows_transitions(self):
        return False

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        pass

    def handle_input(self, input_type):
        pass        
