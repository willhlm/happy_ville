import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='collide':
            self.enter_state('Collided')

class Collided(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.alpha = 255

    def update(self):
        self.alpha *= 0.9
        self.entity.image.set_alpha(self.alpha)
        if self.alpha < 5:
            self.entity.kill()
