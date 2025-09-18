import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        #self.dir = self.entity.dir.copy()

    def update(self, dt):
        pass
    
    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.hitbox[2] = 0
        self.entity.hitbox[3] = 0
        self.time = 0

    def update(self, dt):
        self.time += dt
        if self.time > self.entity.frequency:
            self.enter_state('Active')

    def handle_input(self,input):
        if input == 'Active':
            self.enter_state('Active')

class Active(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.hitbox[2] = 32
        self.entity.hitbox[3] = 32
        self.time = 0

    def update(self, dt):
        self.time += dt
        if self.time > self.entity.frequency:
            if self.entity.frequency < 0: return
            self.enter_state('Idle')

    def handle_input(self,input):
        if input == 'Idle':
             self.enter_state('Idle')

