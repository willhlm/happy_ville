import sys, random

class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.entity.state=str(type(self).__name__).lower()#the name of the class
        self.entity.animation.frame = 0

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

class Idle(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Hurt':
             self.enter_state('Hurt')
        elif input == 'Death':
             self.enter_state('Death')
        elif input == 'Idle':
             self.enter_state('Idle')

class Hurt(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.done = False

    def update(self):
        if self.entity.animation.frame == 0 and self.done:#if animation is finished
            self.enter_state('Death')
        self.done = True

    def handle_input(self,input):
        if input == 'Death':
            self.enter_state('Death')
        elif input=='Idle':
             self.enter_state('Idle')

class Death(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.enter_state('Idle')
        if input=='Hurt':
             self.enter_state('Hurt')
