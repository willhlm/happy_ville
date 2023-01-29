import sys, random
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

    def update_state(self):
        pass

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        #self.stay_still()

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        #self.walk()

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.entity.dead()
