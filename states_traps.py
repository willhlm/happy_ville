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
        if input == 'Death':
             self.enter_state('Death_pre')
        elif input == 'Once':
            self.enter_state('Once_pre')

class Once_pre(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Once_main')

class Once_main(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)#spawn a sword
        self.atatck = self.entity.hurt_box(self.entity)
        self.entity.game_objects.eprojectiles.add(self.atatck)

    def increase_phase(self):
        self.enter_state('Idle')
        self.atatck.kill()

class Death_pre(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Death_main')

class Death_main(Basic_states):#spawn a sword
    def __init__(self,entity):
        super().__init__(entity)
        self.atatck = self.entity.hurt_box(self.entity)
        self.entity.game_objects.eprojectiles.add(self.atatck)

    def increase_phase(self):
        self.entity.kill()
        self.atatck.kill()
