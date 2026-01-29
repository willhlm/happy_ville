import sys, random

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

    def handle_input(self,input,**kwarg):
        if input == 'hurt':
            self.enter_state('hurt') 

class Grow(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.grow_speed = 0.001

    def update_render(self, dt):
        self.entity.radius += dt * self.grow_speed
        self.entity.radius = min(self.entity.radius, 1)
        if self.entity.radius >= 0.4:
            self.grow_speed = 0.005

        if self.entity.radius >= 1:
            self.entity.game_objects.signals.emit('ability_ball_grown')
            self.enter_state('idle')     

    def handle_input(self,input,**kwarg):
        if input == 'hurt':
            self.enter_state('hurt') 

class Hurt(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 0
        self.scale = 0.93
        self.amplitude = 0.2
        self.flashed = False

    def update(self, dt):
        if self.time <= 20:
            self.entity.flash += dt * 0.05
            self.entity.flash = min(self.entity.flash, 1)
        else:
            self.entity.flash -= dt * 0.1
            self.entity.flash = max(self.entity.flash, 0)
        self.amplitude *= self.scale
        self.entity.shake = [random.uniform(-self.amplitude,self.amplitude), random.uniform(-self.amplitude,self.amplitude)]
        
        self.time += dt
        if self.time > 30:
            if self.entity.radius < 1:
                self.enter_state('grow')
            else:
                self.enter_state('idle')
            self.entity.flash = 0

class Death(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
  
    def update_render(self, dt):
        self.entity.explosion += dt * 0.04
        self.entity.explosion = min(self.entity.explosion , 1)
        if self.entity.explosion >= 1:
            self.entity.kill()
