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
        self.time = 0

    def update(self):
        self.play_sfx()
        self.init_time += 0.02*self.entity.game_objects.game.dt
        self.entity.walk(self.init_time)
        if abs(self.entity.velocity[0]) < 0.01:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'attack':
            self.enter_state('Attack_pre')

    def play_sfx(self):
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.time = 100
            self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'][0], vol = 0.05)        

class Attack_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Attack_main')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class Attack_main(Enemy_states):#taiatari
    def __init__(self,entity):
        super().__init__(entity)        
        self.duration = 50
        distance = (self.entity.AI.player_distance[1]**2 + self.entity.AI.player_distance[0]**2)**0.5
        if distance == 0: distance = 1
        ratio = [abs(self.entity.AI.player_distance[0])/distance, abs(self.entity.AI.player_distance[1])/distance]
        self.velocity = [ratio[0] * 4 * sign(self.entity.AI.player_distance[0]), ratio[1] * 4 * sign(self.entity.AI.player_distance[1])]

    def update(self):
        self.entity.velocity = self.velocity.copy()
        self.duration -= self.entity.game_objects.game.dt
        if self.duration < 0:
            self.enter_state('Idle')
            self.entity.AI.handle_input('finish_attack')

    def increase_phase(self):
        pass

    def handle_input(self,input):
        if input == 'collision':#collision with walls -> alla alkbar sends this input
            self.enter_state('Death')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.killed()

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.dead()
