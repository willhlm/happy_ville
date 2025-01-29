import sys, random
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.01 or abs(self.entity.velocity[1]) > 0.01:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) < 0.01 and abs(self.entity.velocity[1]) < 0.01:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class Blink_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.aggro = False#do not collide with player

    def increase_phase(self):
        self.enter_state('Blink_main')

class Blink_main(Enemy_states):#invisible
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.aggro = False#do not collide with player

    def increase_phase(self):
        self.enter_state('Blink_post')

class Blink_post(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.AI.teleport()
        self.entity.aggro = False#do not collide with player

    def increase_phase(self):
        self.entity.aggro = True
        self.enter_state('Idle')
        self.entity.AI.finish()

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.dead()
