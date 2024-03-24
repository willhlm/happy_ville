import sys, math, random
from states_entity import Entity_States

class Weather_States():
    def __init__(self,entity):
        self.entity = entity

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

class Idle(Weather_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        rand=random.randint(1, 1000)
        if rand==0:
            self.enter_state('Wind')

class Wind(Weather_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.blow()

    def handle_input(self,input):
        if input == 'Finish':
            self.enter_state('Idle')
