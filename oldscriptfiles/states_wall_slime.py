import sys
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]
        self.on_ground = False

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

    def update_state(self):
        pass

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if self.entity.collision_types['bottom']:
             self.enter_state('Walk_up')

        elif self.entity.collision_types['left']:
             self.enter_state('Walk_right')

        elif self.entity.collision_types['top']:
             self.enter_state('Walk_down')

        elif self.entity.collision_types['right']:
             self.enter_state('Walk_left')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input =='Attack':
             self.enter_state('Attack')

class Walk_up(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration=[0,1]#gravty
        self.entity.dir = [1,0]
        self.dir = [1,0]

    def update_state(self):
        if self.entity.collision_types['bottom']:#need to land first
            self.on_ground = True

        elif self.on_ground:#right side
            self.enter_state('Walk_right')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack')

class Walk_down(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration=[0,-1]
        self.entity.dir = [-1,0]
        self.dir = [-1,0]

    def update_state(self):
        if self.entity.collision_types['top']:#need to land first
            self.on_ground = True

        elif self.on_ground:#right side
            self.enter_state('Walk_left')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack')

class Walk_left(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration=[1,0]
        self.entity.dir = [0,1]
        self.dir = [0,1]

    def update_state(self):
        if self.entity.collision_types['right']:#need to land first
            self.on_ground = True

        elif self.on_ground:#right side
            self.enter_state('Walk_up')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack')

class Walk_right(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration=[-1,0]
        self.entity.dir = [0,-1]
        self.dir = [0,-1]

    def update_state(self):
        if self.entity.collision_types['left']:#need to land first
            self.on_ground = True

        elif self.on_ground:#right side
            self.enter_state('Walk_down')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.loots()
            self.entity.death()

    def increase_phase(self):
        self.done=True

class Hurt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

class Stun(Enemy_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

class Attack(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        self.done=False
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.attack.lifetime=10

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            attack=self.entity.attack(self.entity)#make the object
            self.entity.projectiles.add(attack)#add to group but in main phase
        elif self.phase=='main':
            self.done=True
