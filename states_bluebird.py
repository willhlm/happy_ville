import sys, random
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
        elif input=='Fly':
             self.enter_state('Fly')
        elif input=='Eat':
             self.enter_state('Eat')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input=='Fly':
             self.enter_state('Fly')
        elif input=='Eat':
             self.enter_state('Eat')

class Eat(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def handle_input(self,input):
        if input=='Fly':
             self.enter_state('Fly')

    def increase_phase(self):
        self.enter_state('Idle')


class Fly(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration=[0,0]
        self.entity.friction=[0,0]
        self.lifetime=200
        rand=random.randint(2,7)
        sign=random.choice([-1,1])
        self.dir[0]=sign
        self.entity.velocity=[sign*rand,-rand]

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.entity.kill()

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.death()

    def increase_phase(self):
        self.done=True
