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

    def update_state(self):
        if abs(self.entity.game_objects.weather.wind.velocity[0]) > 0:
            self.enter_state('Wind')

class Wind(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.blowing()

    def update_state(self):
        if self.entity.game_objects.weather.wind.velocity[0] == 0:
            self.enter_state('Idle')
