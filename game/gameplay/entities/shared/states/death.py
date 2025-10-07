from .base_state import BaseState

class Death(BaseState):
    def __init__(self, entity, deciders, **kwarg):
        super().__init__(entity, deciders)
        self.entity.animation.play('death', 0.2)

    def update_logic(self, dt):
        self.entity.velocity[0] = 0

    def enter_state(self, newstate, **kwarg):
        pass

    def increase_phase(self):
        self.entity.dead()

    def handle_input(self, input_type):
        pass        