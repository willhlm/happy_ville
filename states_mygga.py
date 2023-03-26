import sys, random, math
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

    def update(self):
        self.update_state()

    def update_state(self):
        pass

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        #self.stay_still()

    def update_state(self):
        if abs(self.entity.velocity[0]) > 0.01:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input == 'explode':
            self.enter_state('Pre_explode')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init_time = 0

    def update_state(self):
        self.init_time += 0.02*self.entity.game_objects.game.dt
        amp = min(abs(self.entity.velocity[0]),0.3)
        self.entity.velocity[1] += amp*math.sin(5*self.init_time)# - self.entity.dir[1]*0.1

        if abs(self.entity.velocity[0]) < 0.01:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'explode':
            self.enter_state('Pre_explode')

class Pre_explode(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        player_distance = [self.entity.AI.black_board['target'].rect.centerx-self.entity.rect.centerx,self.entity.AI.black_board['target'].rect.centery-self.entity.rect.centery]#check plater distance
        self.entity.AI.black_board['player_distance'] = player_distance

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

    def update_state(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.AI.handle_input('De_explode')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.suicide()

    def update_state(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.dead()
        self.entity.AI.handle_input('Attack')
