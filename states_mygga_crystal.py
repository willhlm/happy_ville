import sys, math
from states_entity import Entity_States

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.01:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input == 'attack':
            self.enter_state('Attack_pre')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init_time = 0

    def update(self):
        self.init_time += 0.02*self.entity.game_objects.game.dt
        self.entity.walk(self.init_time)
        if abs(self.entity.velocity[0]) < 0.01:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'attack':
            self.enter_state('Attack_pre')

class Attack_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Attack_main')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class Attack_main(Enemy_states):#taiatari
    def __init__(self,entity):
        super().__init__(entity)  
        self.entity.attack()      

    def increase_phase(self):
        self.entity.AI.handle_input('finish_attack')
        self.enter_state('Idle')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.killed()

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.dead()
