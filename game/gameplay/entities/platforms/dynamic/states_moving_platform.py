import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class        

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self, dt):
        pass

    def increase_phase(self):#called when animation is finished in reset_timer
        pass

    def handle_input(self,input,**kwarg):
        pass     

class Off(Basic_states):#idle
    def __init__(self,entity):
        super().__init__(entity)        
        self.entity.velocity[0] = 0

    def handle_input(self,input,**kwarg):
        if input == 'transform' or input == 'On':
            self.enter_state('On')   

class On(Basic_states):#on
    def __init__(self,entity,**kwarg):
        super().__init__(entity)

    def update(self, dt):
        self.entity.velocity[0] += dt * 0.01

    def handle_input(self,input,**kwarg):
        if input == 'transform' or input == 'Off':
            self.enter_state('Off')   

