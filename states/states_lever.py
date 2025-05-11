import sys

class Basic_states():
    def __init__(self,entity, **kwarg):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class        

    def update(self):
        pass

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class Off(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)        

    def handle_input(self,input):
        if input== 'Transform':
            self.enter_state('Transform_on')

class Transform_on(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)        

    def increase_phase(self):
        self.enter_state('On')

class Transform_off(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)        

    def increase_phase(self):
        self.enter_state('Off')        

class On(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)

    def handle_input(self,input):
        if input== 'Transform':
            self.enter_state('Transform_off')            
