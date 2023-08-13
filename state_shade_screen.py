import sys, random
from states_entity import Entity_States

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.state_name = str(type(self).__name__).lower()#the name of the class

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys


class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Turn':
            self.enter_state('Turn')

class Turn(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        

    def update(self):
        self.entity.image.fill()

    def handle_input(self,input):
        if input == 'Turn_back':
            self.enter_state('Idle')
