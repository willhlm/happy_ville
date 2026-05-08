from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Contained(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('hanging')        

    def update_logic(self, dt):
        pass
