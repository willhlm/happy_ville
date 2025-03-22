import sys

class Idle():
    def __init__(self,entity):
        self.entity = entity

    def update(self):#notmal, do nothing
        self.entity.update_vel()
        self.entity.currentstate.update()#need to be aftre update_vel since some state transitions look at velocity
        self.entity.animation.update()#need to be after currentstate since animation will animate the current state        
        self.entity.shader_state.update()#need to be after animation       

    def enter_state(self, newstate, **kwarg):
        self.entity.hitstop_states = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

class Stop(Idle):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.lifetime = kwarg.get('lifetime', 100)
        self.call_back = kwarg.get('call_back', None)

    def update(self):
        self.entity.velocity = [0,0]
        self.lifetime -= self.entity.game_objects.game.dt
        if self.lifetime < 0:
            if self.call_back: self.call_back()
            self.enter_state('Idle')