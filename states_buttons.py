import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class A_idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'press':
            self.enter_state('A_select')

class A_select(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('A_press')

class A_press(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('A_idle')

class B_idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'press':
            self.enter_state('B_select')

class B_select(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('B_press')

class B_press(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('B_idle')
