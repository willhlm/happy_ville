from .base_state import BaseState

class Wait(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        self.wait_time = kwargs.get('time', 50)
        self.next_state = kwargs.get('next_state', 'patrol')
        
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("idle", 0.2)
        self.kwargs = kwargs

    def update(self, dt):
        self.wait_time -= dt
        if self.wait_time <= 0:
            self.enter_state(self.next_state, **self.kwargs)

    def update_logic(self, dt):
        pass  # No movement logic

    def handle_input(self, input_type):
        if input_type == "Hurt":
            self.enter_state("chase")   