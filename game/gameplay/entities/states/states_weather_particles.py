import sys, math, random
from gameplay.entities.states.states_entity import Entity_States

class Weather_States(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Weather_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        rand=random.randint(0, self.entity.trans_prob)
        if rand==1:
            self.enter_state('Flip')

class Flip(Weather_States):
    def __init__(self,entity):
        super().__init__(entity)
        #self.entity.velocity[1]=self.entity.velocity[1]*0.8#slow down
        #self.entity.velocity[0]=self.entity.velocity[0]*0.8

    def increase_phase(self):
        self.enter_state('Idle')
