import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.state = type(self).__name__.lower()#the name of the class
        self.entity.animation.reset_timer()

    def update(self):
        pass       

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished in reset_timer
        pass

    def handle_input(self,input,**kwarg):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.health = 1#set it back

    def handle_input(self,input):
        if input=='Hurt':
             self.enter_state('Hurt')
        elif input == 'Death':
             self.enter_state('Death')
        elif input == 'Idle':
             self.enter_state('Idle')

class Hurt(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Death':
            self.enter_state('Death')
        elif input=='Idle':
             self.enter_state('Idle')

    def increase_phase(self):
        if self.entity.health == 0.5:
            self.enter_state('Half')
        else:
            self.enter_state('Death')

class Half(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.enter_state('Idle')
        if input=='Hurt':
             self.enter_state('Hurt')

class Death(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.enter_state('Idle')
