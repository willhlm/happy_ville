import sys
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.2:
            self.enter_state('Jump')

    def handle_input(self,input):
        if input=='taunt':
             self.enter_state('Taunt')
        elif input == 'fade':
            self.enter_state('Fade')

class Taunt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.2:
            self.enter_state('Jump')

    def handle_input(self,input):
        if input == 'jump':
            self.enter_state('Jump')
        elif input == 'idle':
            self.enter_state('Idle')
        elif input == 'fade':
            self.enter_state('Fade')

class Jump(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1] -= 6#jump

    def update(self):
        if abs(self.entity.velocity[0]) <= 0.2:
            self.enter_state('Idle')

    def increase_phase(self):
        self.entity.AI.handle_input('landed')

class Fade(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader_state.enter_state('Dissolve',colour = [0.5,0.6,0.8,1])
        self.entity.invincibile = True

    def update(self):        
        if self.entity.shader_state.time >= 1:
            self.entity.kill()

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader_state.enter_state('Dissolve',colour = [0.9,0.2,0.1,1])

    def update(self):        
        if self.entity.shader_state.time >= 1:
            self.entity.dead()            
