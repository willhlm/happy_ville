import sys
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

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

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input =='Attack':
             self.enter_state('Attack_pre')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack_pre')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.entity.dead()

class Hurt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.enter_state('Idle')

class Stun(Enemy_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
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
        attack=self.entity.attack(self.entity)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.attack.lifetime=10

    def increase_phase(self):
        self.enter_state('Idle')

class Ambush_pre(Attack_pre):
    def __init__(self,entity):
        super().__init__(entity)

class Ambush_main(Attack_main):
    def __init__(self,entity):
        super().__init__(entity)
