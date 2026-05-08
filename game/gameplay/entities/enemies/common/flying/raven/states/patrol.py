from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Patrol(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.fall_speed = entity.config['speeds']['fall']
        self.fall_max = entity.config['speeds']['fall_max']
        self.ground_snap = entity.config['speeds']['ground_snap']
        self.entity.animation.play('idle', 0.16)

    def update_logic(self, dt):
        self.entity.velocity[0] = 0
        if self.entity.is_on_floor():
            self.entity.velocity[1] = self.ground_snap
        else:
            self.entity.velocity[1] = min(self.entity.velocity[1] + dt * self.fall_speed, self.fall_max)
