from .base_state import BaseState
import random

class Patrol(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("walk", 0.17)
        self.patrol_speed = self.entity.config['speeds']['patrol']
        self.entity.velocity[0] = self.patrol_speed
        
        value = random.choice([-1, 1])#if no dir is apped, then take either -1 or 1
        self.entity.dir[0] *=  kwargs.get('dir',value) 

    def update_logic(self, dt):
        self.entity.velocity[0] += self.entity.dir[0] * self.patrol_speed