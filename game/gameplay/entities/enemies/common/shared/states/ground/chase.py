import random
from ..base_state import BaseState
from engine.utils import functions

class GroundChase(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("walk")
        self.stop_distance = kwargs.get('stop_distance', 30)
        self.chase_speed = entity.config['speeds']['chase']
        
    def update_logic(self, dt):       
        # Chase if beyond stopping distance
        if abs(self.player_distance[0]) > self.stop_distance:#don't get closer than stop distance
            self.look_target()
            self.entity.velocity[0] += self.entity.dir[0] * self.chase_speed
        else:
            pass

    def look_target(self):
        self.entity.dir[0] = functions.sign(self.player_distance[0])