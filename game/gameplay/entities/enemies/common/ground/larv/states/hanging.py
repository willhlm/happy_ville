from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Hanging(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('hang', 0.15)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
        self.entity.hanging_component.update_hanging_motion(dt)

    def handle_input(self, input_type):
        if input_type == 'drop':
            self.entity.flags['aggro'] = True
            self.entity.currentstate.enter_state('fall')
