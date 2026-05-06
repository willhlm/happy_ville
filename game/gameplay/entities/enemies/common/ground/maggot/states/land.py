from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Land(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("land")

    def update_logic(self, dt):
        self.entity.velocity[0] = 0

    def increase_phase(self):
        state_cfg = self.entity.config["states"].get(self.config_key, {})
        next_state = state_cfg.get("next_state", "wait")
        kwargs = state_cfg.get("kwargs", {})
        self.enter_state(next_state, **kwargs)
