# orthogonal_torpedo/states/chase_torpedo.py
import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState
from engine.utils import functions

class Chase(BaseState):
    """Chase that positions above player before attacking"""
    
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("walk")
        self.chase_speed = entity.config['speeds']['chase']
        self.target_height_above = kwargs.get('target_height', 80)  # 80px above player
        self.horizontal_tolerance = kwargs.get('h_tolerance', 20)
        
    def update_logic(self, dt):
        # Calculate desired position (above player)
        desired_x = self.player_distance[0]  # Align horizontally with player
        desired_y = self.player_distance[1] - self.target_height_above  # Position above
        
        # Check if in attack position
        if (abs(desired_x) < self.horizontal_tolerance and 
            self.player_distance[1] > 20):  # Player is below us
            # In position - deciders will handle attack decision
            self.entity.velocity[0] *= 0.9  # Slow down horizontally
            self.entity.velocity[1] *= 0.9
            return
        
        # Move toward desired position
        distance = (desired_x**2 + desired_y**2)**0.5
        if distance > 5:
            ratio = [desired_x/distance, desired_y/distance]
            self.entity.velocity[0] += ratio[0] * self.chase_speed
            self.entity.velocity[1] += ratio[1] * self.chase_speed
        
        self.look_target()
                
    def look_target(self):
        self.entity.dir[0] = functions.sign(self.player_distance[0])