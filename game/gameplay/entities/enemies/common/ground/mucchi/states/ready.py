from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Ready(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('ready', 0.2)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
