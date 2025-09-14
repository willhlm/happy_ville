import sys
from gameplay.entities.states.states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.hitbox[2] = 0
        self.entity.hitbox[3] = 0
        self.time = 0

    def update(self):
        self.time += self.entity.game_objects.game.dt
        if self.time > self.entity.frequency:
            self.enter_state('Active')

    def handle_input(self,input):
        if input == 'Active':
            self.enter_state('Active')

class Active(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.hitbox[2] = 32
        self.entity.hitbox[3] = 32
        self.time = 0

    def update(self):
        self.time += self.entity.game_objects.game.dt
        if self.time > self.entity.frequency:
            if self.entity.frequency < 0: return
            self.enter_state('Idle')

    def handle_input(self,input):
        if input == 'Idle':
             self.enter_state('Idle')

