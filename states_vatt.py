import sys
from states_entity import Entity_States
import random
#from Entities import Vatt

class Vatt_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def update_state(self):
        pass

class Idle(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_pre')

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Run':
            self.enter_state('Run')
        elif input == 'Walk':
            self.entity.dir[0] = random.choice((1,-1))
            self.enter_state('Walk')
        elif input == 'Transform':
            self.enter_state('Transform')

class Idle_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_aggro_pre')

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt_aggro')
        elif input == 'Run':
            self.enter_state('Run_aggro')

class Walk(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.entity.acceleration[0] = 0.4

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Idle':
            self.enter_state('Idle')
        elif input == 'Transform':
            self.enter_state('Transform')

class Fall_stand_pre(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self, input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Transform':
            self.enter_state('Transform')
        elif input == 'Ground':
            self.enter_state('Idle')

class Fall_stand_main(Fall_stand_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

class Fall_stand_aggro_pre(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self, input):
        if input=='Hurt':
            self.enter_state('Hurt_aggro')
        elif input == 'Ground':
            self.enter_state('Idle_aggro')

class Fall_stand_aggro_main(Fall_stand_aggro_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

class Run(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 1.5

    def update_state(self):
        pass

    def handle_input(self, input):
        if input == 'Run':
            pass
        elif input == 'Transform':
            self.enter_state('Transform')
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Run_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 1.2

    def handle_input(self, input):
        if input == 'Run':
            pass
        elif input == 'Javelin':
            self.enter_state('Javelin_pre')

class Death(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.entity.dead()

class Hurt(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        print('hurt')

    def increase_phase(self):
        self.enter_state('Transform')

class Hurt_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.enter_state('Idle')

class Transform(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.enter_state('Idle_aggro')
        self.entity.AI_stack[-1].handle_input('Aggro')
        if not self.entity.aggro:
            self.entity.turn_clan()

class Stun(Vatt_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

class Javelin_pre(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration = [0,0]
        self.entity.velocity = [0,0]
        self.counter = 0
        self.pre_pos_increment = [-3,-2,-1,-1,-1,-1]

    def update_state(self):
        self.counter += 1
        if int(self.counter/4) >= len(self.pre_pos_increment):
            pass
        elif self.counter%4 == 0:
            self.entity.update_pos((0,self.pre_pos_increment[int(self.counter/4)]))

    def increase_phase(self):
        self.enter_state('Javelin_main')
        self.entity.acceleration = [3.5,0]

class Javelin_main(Javelin_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.counter += 1
        if self.counter > 24:
            self.enter_state('Javelin_post')

    def increase_phase(self):
        pass

class Javelin_post(Javelin_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        pass

    def increase_phase(self):
        self.enter_state('Fall_stand_aggro_pre')
