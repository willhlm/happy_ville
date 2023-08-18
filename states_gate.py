import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input== 'Transform':
            self.enter_state('Transform')


class Transform(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.hitbox[2] = 0
        self.entity.hitbox[3] = 0

    def increase_phase(self):
        self.enter_state('Interacted')

class Interacted(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
