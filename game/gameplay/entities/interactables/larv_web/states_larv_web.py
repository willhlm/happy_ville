import sys, random

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished
        pass

    def update(self, dt):
        pass
    
    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        player = self.entity.game_objects.player.hitbox
        dx = player.centerx - self.entity.anchor_pos[0]
        dy = player.centery - (self.entity.anchor_pos[1] )
        if abs(dx) < self.entity.trigger_distance[0] and abs(dy) < self.entity.trigger_distance[1]:
            self.entity.larv.trigger_drop()
            self.enter_state('Dropped')        

class Dropped(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
