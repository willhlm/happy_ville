import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class

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
        if input == 'transform':
            self.enter_state('Transform')

class Transform(Basic_states):#runestone
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Interacted')

class Interacted(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.player.currentstate.handle_input('pray_post')
