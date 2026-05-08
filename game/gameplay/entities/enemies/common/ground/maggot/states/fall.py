from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Fall(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("fall")

    def update_logic(self, dt):
        self.entity.velocity[0] = 0
        if self.entity.is_on_floor():
            self.enter_state("land")
