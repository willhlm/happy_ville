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

    def handle_input(self,input,**kwarg):
        if input=='active':
            self.enter_state('Active')

class Active(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.game_objects.player.currentstate.handle_input('Pray_post')

class Outline(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input,**kwarg):
        if input=='active':
            self.enter_state('Active')

    def increase_phase(self):
        self.enter_state('Idle')

