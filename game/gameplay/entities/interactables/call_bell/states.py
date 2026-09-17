import sys

class Basic_states():
    def __init__(self,entity, **kwarg):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class        

    def update(self, dt):
        pass

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class Idle(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)        

    def handle_input(self, input):
        if input == 'Ring':
            self.enter_state('Ring')
            self.entity.emit_signal()

class Ring(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)        

    def increase_phase(self):
        self.enter_state('Idle')

