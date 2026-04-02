from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Land(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('land', 0.18)

    def update_logic(self, dt):
        self.entity.velocity[0] *= 0.8
        self.entity.velocity[1] = self.entity.config['speeds']['ground_snap']

    def increase_phase(self):
        self.enter_state('wait', time = self.entity.config['timers']['hang_drop_delay'], next_state = 'patrol')
