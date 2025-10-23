from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class Sleep(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("sleep")

    def update_logic(self, dt):
        pass