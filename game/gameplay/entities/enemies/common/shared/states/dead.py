from .base_state import BaseState

class Dead(BaseState):
    def __init__(self, entity, deciders, config_key, **kwarg):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('dead', 0.2)
        self.corpse_time = 20
        self.fade_started = False

    @property
    def allows_transitions(self):
        return False

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
        if self.fade_started:
            return

        self.corpse_time -= dt
        if self.corpse_time <= 0:
            self.fade_started = True
            self.entity.dead()

    def handle_input(self, input_type):
        pass

    def increase_phase(self):
        pass
