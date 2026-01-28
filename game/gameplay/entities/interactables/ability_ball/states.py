import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def update(self, dt):
        pass    
        
    def update_render(self, dt):
        pass               

    def enter_state(self,newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate.capitalize())(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished in reset_timer
        pass

    def handle_input(self,input,**kwarg):
        pass

    def draw(self, target):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

class Grow(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_render(self, dt):
        self.entity.radius += dt * 0.04
        self.entity.radius = min(self.entity.radius, 1)
        if self.entity.radius >= 1:
            self.enter_state('idle')     

class Hurt(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 0

    def update(self, dt):
        self.time += dt
        if self.time > 50:
            self.enter_state('idle')

class Death(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
  
    def update_render(self, dt):
        self.entity.explosion += dt * 0.04
        self.entity.explosion = min(self.entity.explosion , 1)
        if self.entity.explosion >= 1:
            self.entity.kill()
