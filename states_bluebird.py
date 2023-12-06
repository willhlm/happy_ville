import sys, random
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
        if input=='Walk':
             self.enter_state('Walk')
        elif input=='Fly':
             self.enter_state('Fly')
        elif input=='Eat':
             self.enter_state('Eat')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

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

    def update(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.entity.kill()

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.dead()
