import sys, random
from gameplay.entities.states.states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        pass

    def increase_phase(self):#enter wind state when animation is finished to make a smooth transition
        if abs(self.entity.game_objects.weather.wind.velocity[0]) > 0:
            self.enter_state('Wind')

class Wind(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.timer = random.randint(40,60)

    def update(self, dt):
        self.timer -= dt
        if self.timer < 0:
            self.entity.blowing()
            self.timer = random.randint(40,60)

    def increase_phase(self):#enter wind state when animation is finished to make a smooth transition
        if self.entity.game_objects.weather.wind.velocity[0] == 0:
            self.enter_state('Idle')
