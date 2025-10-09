from gameplay.entities.shared.states.enemy.base_state import BaseState

class WakeUp(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("wake_up")
        self.next_state = kwargs.get('next_state', 'chase')

    def update_logic(self, dt):
        pass

    def increase_phase(self):
        self.enter_state(self.next_state)