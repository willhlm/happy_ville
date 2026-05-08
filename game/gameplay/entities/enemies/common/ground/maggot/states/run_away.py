from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class RunAway(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("walk")
        self.run_speed = entity.config["speeds"]["run_away"]
        self.dir_multiplier = kwargs.get("dir")
        self.escape_dir_initialized = False

    def update_logic(self, dt):
        self._initialize_escape_direction()
        self.entity.velocity[0] += dt * self.entity.dir[0] * self.run_speed

    def _initialize_escape_direction(self):
        if self.escape_dir_initialized:
            return

        if self.dir_multiplier is not None:
            self.entity.dir[0] *= self.dir_multiplier
        else:
            self.entity.dir[0] = -1 if self.player_distance[0] >= 0 else 1

        self.escape_dir_initialized = True
