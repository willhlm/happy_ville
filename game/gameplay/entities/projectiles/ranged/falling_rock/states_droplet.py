import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(str(type(self).__name__).lower())#the name of the class  

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate.capitalize())(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished in reset_timer
        pass

    def handle_input(self,input,**kwarg):
        pass

    def update(self, dt):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)    

    def update(self, dt):
        self.entity.velocity[1] += dt
        self.entity.velocity[1] = min(7,self.entity.velocity[1])

    def handle_input(self,input,**kwarg):
        if input=='death':            
            self.enter_state('death')

class Death(Basic_states):#idle once
    def __init__(self,entity):
        super().__init__(entity)        

    def update(self, dt):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.kill()