import sys, random

from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.health = 1#set it back

    def handle_input(self,input):
        if input=='Hurt':
             self.enter_state('Hurt')
        elif input == 'Death':
             self.enter_state('Death')
        elif input == 'Idle':
             self.enter_state('Idle')

class Hurt(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Death':
            self.enter_state('Death')
        elif input=='Idle':
             self.enter_state('Idle')

    def increase_phase(self):
        if self.entity.health == 0.5:
            self.enter_state('Half')
        else:
            self.enter_state('Death')

class Half(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.enter_state('Idle')
        if input=='Hurt':
             self.enter_state('Hurt')

class Death(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.enter_state('Idle')
