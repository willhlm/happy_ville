import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate.capitalize())(self.entity)#make a class based on the name of the newstate: need to import sys

    def set_animation_name(self, name):
        self.entity.state = name

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        if random.randint(0,100) == 0:
            self.enter_state('Transform')

class Transform(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.drop()
        self.enter_state('Dropped')

class Dropped(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')
