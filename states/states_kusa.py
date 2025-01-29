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

    def handle_input(self,input):
        if input=='Transform':
             self.enter_state('Transform')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle_aggro')
        elif input =='Attack':
             self.enter_state('Death')

class Transform(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1]=-7

    def increase_phase(self):
        self.enter_state('Idle_aggro')

class Idle_aggro(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input =='Attack':
             self.enter_state('Death')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.suicide()

    def increase_phase(self):
        self.entity.dead()

class Hurt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')

class Stun(Enemy_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.lifetime=duration

    def update(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

    def change_state(self,input):
        pass
