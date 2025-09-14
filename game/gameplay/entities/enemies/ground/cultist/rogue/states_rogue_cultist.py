import sys
from gameplay.entities.states.states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.2:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input =='Attack':
             self.enter_state('Attack_pre')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) <= 0.2:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack_pre')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

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

class Attack_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction

    def increase_phase(self):
        self.enter_state('Attack_main')

class Attack_main(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.attack()

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.AI.handle_input('Finish_attack')

class Ambush_pre(Attack_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Ambush_main')

class Ambush_main(Attack_main):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')
