import random
from ..base_state import BaseState
from engine.utils import functions

class FlyingChase(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("walk")
        self.stop_distance = kwargs.get('stop_distance', 30)
        self.chase_speed = entity.config['speeds']['chase']
            
    def update_logic(self, dt):
        if abs(self.target_distance[0]) > self.stop_distance or abs(self.target_distance[1]) > self.stop_distance:#chase up to stop distance
            self.look_target()
            
            # Chase in both X and Y
            distance = (self.target_distance[0]**2 + self.target_distance[1]**2)**0.5
            if distance == 0:
                return
            # Normalize direction
            ratio = [self.target_distance[0]/distance, self.target_distance[1]/distance]
            self.entity.velocity[0] += dt * ratio[0] * self.chase_speed
            self.entity.velocity[1] += dt * ratio[1] * self.chase_speed
                
    def look_target(self):
        self.entity.dir[0] = functions.sign(self.target_distance[0]) or self.entity.dir[0]
