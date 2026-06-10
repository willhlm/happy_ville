import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity        

    def update(self, dt):
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
        self.entity.animation.play('idle')

    def handle_input(self,input,**kwarg):
        if input == 'grow':
            self.enter_state('Grow')
        elif input == 'death':
            self.enter_state('Death')

class Grow(Basic_states):#idle once
    def __init__(self,entity):
        super().__init__(entity)        
        self.entity.animation.play('grow')

    def increase_phase(self):
        self.enter_state('Grown')

    def handle_input(self,input,**kwarg):
        if input == 'death':
            self.enter_state('Death')

class Grown(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)        
        self.entity.animation.play('grown')

    def handle_input(self,input,**kwarg):
        if input == 'death':
            self.enter_state('Death')

class Death(Basic_states):#idle once
    def __init__(self,entity):
        super().__init__(entity)   
        self.entity.animation.play('death')     

    def increase_phase(self):
        self.entity.kill()
