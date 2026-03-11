import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        #self.dir = self.entity.dir.copy()

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished
        pass

    def update(self, dt):
        pass
    
    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input,**kwarg):
        if input == 'Interact':
            self.enter_state('Interact')

class Interact(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.turn_on()

    def increase_phase(self):
        self.enter_state('Interacted')

class Interacted(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):#fire place
        if input == 'Interact':
            self.enter_state('Pre_idle')

class Pre_idle(Basic_states):#fire palce
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.turn_off()

    def increase_phase(self):
        self.enter_state('Idle')
