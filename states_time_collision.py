import sys
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def increase_phase(self):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Transition_1':
            self.enter_state('Transition_1')

class Transition_1(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Gone')

class Transition_2(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')

class Gone(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Transition_2':
            self.enter_state('Transition_2')
