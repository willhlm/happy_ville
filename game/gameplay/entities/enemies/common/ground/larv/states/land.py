from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Land(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.set_surface_stick_enabled(True)
        self.entity.set_surface_motion_paused(True)
        self.entity.animation.play('land', 0.18)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state('crawl')
