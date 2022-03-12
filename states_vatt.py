import sys
from states_entity import Entity_States
import random
#from Entities import Vatt

class Vatt_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

    def change_state(self,input):
        self.enter_state(input)

    def update_state(self):
        pass

class Idle(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()


    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand')

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Run':
            self.enter_state('Run')
        elif input == 'Walk':
            self.entity.dir[0] = random.choice((1,-1))
            self.enter_state('Walk')

class Idle_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_aggro')

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt_aggro')
        elif input == 'Run':
            self.enter_state('Run_aggro')


class Walk(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.entity.acceleration[0] = 0.4 * self.entity.dir[0]

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Idle':
            self.enter_state('Idle')
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Fall_stand(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')

    def handle_input(self, input):
        if input=='Hurt':
            self.enter_state('Hurt')

class Fall_stand_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle_aggro')

    def handle_input(self, input):
        if input=='Hurt':
            self.enter_state('Hurt_aggro')

class Run(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 1.5

    def update_state(self):
        pass

    def handle_input(self, input):
        if input == 'Run':
            pass
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Run_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 1.2 * self.entity.dir[0]

    def update_state(self):
        pass

    def handle_input(self, input):
        if input == 'Run':
            pass
        elif input == 'Javelin':
            self.enter_state('Javelin')

class Death(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.loots()
            self.entity.kill()

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Hurt(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Transform')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Hurt_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Transform(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done = False

    def update_state(self):
        pass

    def update_state(self):
        if self.done:
            self.entity.max_vel=5
            self.entity.aggro=True
            type(self.entity).aggro = True
            self.entity.AImethod=self.entity.aggroAI
            self.enter_state('Idle_aggro')

    def increase_phase(self):
        self.done=True

class Stun(Vatt_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

    def change_state(self,input):
        pass

class Javelin(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases = ['pre','main','post']
        self.phase = 'pre'
        self.entity.acceleration = [0,0]
        self.entity.velocity = [0,0]
        self.counter = 0
        self.done = False
        self.pre_pos_increment = [-3,-2,-1,-1,-1,-1]

    def update_state(self):
        if self.phase == 'pre':
            if int(self.counter/4) >= len(self.pre_pos_increment):
                pass
            elif self.counter%4 == 0:
                self.entity.update_pos((0,self.pre_pos_increment[int(self.counter/4)]))
        elif self.phase == 'main':
            if self.counter > 24:
                self.phase = 'post'
        elif self.done:
            self.enter_state('Fall_stand_aggro')
        self.counter += 1

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            self.counter = 0
            self.entity.acceleration = [3.5*self.entity.dir[0],0]
        elif self.phase=='main':
            pass
        elif self.phase=='post':
            self.done=True

    def handle_input(self, input):
        pass
