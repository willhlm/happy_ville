import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def update(self):
        pass       

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished in reset_timer
        pass

    def handle_input(self,input,**kwarg):
        pass

class Idle(Basic_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('idle')

class Wild(Basic_states):#idle once
    def __init__(self, entity, **kwarg):
        super().__init__(entity)        
        self.entity.animation.play('wild')
        velocity = kwarg.get('velocity', [2, -4])
        velocity_range = kwarg.get('velocity_range', [1, 0])#plus minus the velocity
        self.entity.velocity = [random.uniform(velocity[0] - velocity_range[0], velocity[0] + velocity_range[0]),random.uniform(velocity[1] - velocity_range[1], velocity[1] + velocity_range[1])]
        self.entity.hitbox = self.entity.rect.copy()#light need hitbox
        self.entity.light = self.entity.game_objects.lights.add_light(self.entity, radius = 50)

    def update(self):
        self.entity.twinkle()