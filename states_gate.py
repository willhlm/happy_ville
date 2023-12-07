import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.state_name = str(type(self).__name__).lower()#the name of the class
        self.dir = self.entity.dir

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
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
