from ..base_state import BaseState
import random, math
from engine.utils.functions import sign

class FlyingPatrol(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)       
        self.entity.animation.play("walk")
        self.patrol_speed = self.entity.config['speeds']['patrol']
                
        self._calculate_position()# Calculate patrol target position
        self.time = 0
        
    def update_logic(self, dt):
        self.time += 0.02

        distance = [self.target_position[0] - self.entity.rect.centerx,  self.target_position[1] - self.entity.rect.centery]
        total_distance = (distance[0]**2 + distance[1]**2)**0.5
        ratio = [distance[0]/total_distance, distance[1]/total_distance]
        self.entity.velocity[0] += dt * ratio[0] * self.patrol_speed 
        self.entity.velocity[1] += dt * ratio[1] * self.patrol_speed
                                        
        self._sway(dt)  # Sway animation
    
    def _calculate_position(self):
        """Calculate new random patrol point around spawn"""
        angle = random.randint(0, 180)
        amp = random.randint(40, 80)
        offset = [-20 - 10*self.entity.dir[0], 20 - 10*self.entity.dir[0]]
        angle = random.randint(angle + offset[0], angle + offset[1])
        
        self.target_position = [
            amp * math.cos(math.pi * angle/180) + self.entity.original_pos[0],
            amp * math.sin(math.pi * angle/180) + self.entity.original_pos[1]
        ]
        self._look_target()
    
    def _look_target(self):
        self.entity.dir[0] = sign(self.target_position[0] - self.entity.rect.centerx)

    def _sway(self, dt):
        amp = min(abs(self.entity.velocity[0]),0.3)
        self.entity.velocity[1] += dt * amp * math.sin(5*self.time)# - self.entity.dir[1]*0.1        