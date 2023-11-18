import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update_state(self):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if abs(self.entity.velocity[0]) > 0.0001:
            self.enter_state('Walk')

class Walk(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if abs(self.entity.velocity[0]) <= 0.0001:
            self.enter_state('Idle')

class Fall_stand(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Ground':
            self.enter_state('Land')

class Land(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.AI.enter_AI('Wait',count = 100, next_state = 'Run_away')

class Death(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.dead()
