import sys

class Basic_states():
    def __init__(self,entity, **kwarg):
        self.entity = entity
        self.entity.state = str(type(self).__name__).lower()#the name of the class

    def update(self):
        pass

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class Erect(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.entity.hitbox = self.entity.rect.copy()

    def handle_input(self,input):
        if input == 'Transform' or input == 'Off':
            self.enter_state('Transform_down')

class Transform_down(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)

    def increase_phase(self):
        self.enter_state('Down')

class Transform_up(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)

    def increase_phase(self):
        self.enter_state('Erect')

class Down(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.entity.hitbox[2] = 0
        self.entity.hitbox[3] = 0

    def handle_input(self,input):
        if input == 'Transform' or input == 'On':
            self.enter_state('Transform_up')
