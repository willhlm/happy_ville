import random
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Skip(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("skip")

        self.skip_speed = self.entity.config['speeds']['skip']
        self.entity.velocity[0] = self.skip_speed        
        
        value = random.choice([-1, 1])#if no dir is apped, then take either -1 or 1
        self.entity.dir[0] *=  kwargs.get('dir',value) 
        self.skip = True

    def update_logic(self, dt):        
        self.entity.velocity[0] += dt * self.entity.dir[0] * self.skip_speed
        if self.skip:
            self.entity.velocity[1] = -2
            self.skip = False
        
        
    def handle_input(self, input):
        if input =='Ground':
            self.skip = True
            
