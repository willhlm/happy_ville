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
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

    def change_state(self,input):
        self.enter_state(input)

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
             self.enter_state('Attack')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

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

    def change_state(self,input):
        pass

class Dead(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.entity.death()

    def update_state(self):
        pass

    def increase_phase(self):
        pass

    def change_state(self,input):
        pass

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

    def change_state(self,input):
        pass

class Stun(Enemy_states):
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


class Ambush(Attack):
    def __init__(self,entity):
        super().__init__(entity)
