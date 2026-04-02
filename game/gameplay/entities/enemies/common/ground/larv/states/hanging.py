import math

from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Hanging(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('hang', 0.15)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
        self.entity.hang_phase += self.entity.hang_speed * dt
        sway_x = math.sin(self.entity.hang_phase) * self.entity.hang_sway_x
        sway_y = math.cos(self.entity.hang_phase * 0.5) * self.entity.hang_sway_y
        self.entity.body.set_pos([
            self.entity.anchor_pos[0] + sway_x,
            self.entity.anchor_pos[1] + sway_y,
        ])

    def handle_input(self, input_type):
        if input_type == 'drop':
            self.entity.flags['aggro'] = True
            self.entity.currentstate.enter_state('dropping')
