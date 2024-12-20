import sys
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
        if abs(self.entity.velocity[0]) > 0.01:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input == 'attack':
            self.enter_state('Pre_explode')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init_time = 0
        self.channel = self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'][0], loop = -1)     

    def set_volume(self):
        distance_to_center = ((self.entity.blit_pos[0] - 320)**2 + (self.entity.blit_pos[1]-180) ** 2)**0.5
        max_distance = (320**2 + 180**2)**0.5
        distance = 1 - (distance_to_center / max_distance)            
        self.channel.set_volume(max(0, min(1, distance)))

    def update(self):
        self.set_volume()
        self.init_time += 0.02*self.entity.game_objects.game.dt
        self.entity.walk(self.init_time)
        if abs(self.entity.velocity[0]) < 0.01:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'attack':
            self.enter_state('Pre_explode')

    def enter_state(self, state):
        super().enter_state(state)
        self.channel.fadeout(300)

class Pre_explode(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        player_distance = self.entity.AI.player_distance
        if abs(player_distance[0]) < 50 and abs(player_distance[1]) < 50:
            self.enter_state('Death')
        else:
            self.enter_state('De_explode')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class De_explode(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.AI.handle_input('De_explode')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.killed()

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.dead()
        #self.entity.AI.handle_input('Attack')
