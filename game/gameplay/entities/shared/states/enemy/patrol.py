from .base_state import BaseState

class Patrol(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("walk", 0.17)
        self.entity.velocity[0] = self.entity.patrol_speed
        self.entity.dir[0] *=  kwargs.get('dir', 1)  #change direction before leaving

    def update_logic(self, dt):
        self.entity.velocity[0] += self.entity.dir[0] * self.entity.patrol_speed