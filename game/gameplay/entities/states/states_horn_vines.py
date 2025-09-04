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
        self.delay = 100

    def update(self):
        self.delay -= self.entity.game_objects.game.dt
        if self.delay < 0:
            self.enter_state('Grow')

class Grow(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.hitbox = self.entity.rect.copy()

    def increase_phase(self):
        self.enter_state('Activate')

class Activate(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
