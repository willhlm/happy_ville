from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class Sleep(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("sleep")

    def update_logic(self, dt):
        pass