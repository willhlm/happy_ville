from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Dropping(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('fall', 0.18)

    def update_logic(self, dt):
        self.entity.velocity[0] *= 0.92

    def handle_input(self, input_type):
        if input_type == 'Ground':
            self.enter_state('land')
