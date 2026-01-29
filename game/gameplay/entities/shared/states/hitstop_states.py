import sys

class Idle():
    def __init__(self,entity):
        self.entity = entity

    def update_render(self, dt):#notmal, do nothing        
        self.entity.shader_state.update_render(dt)#need to be after animation

    def update(self, dt):#notmal, do nothing
        self.entity.update_vel(dt)
        self.entity.currentstate.update(dt)#need to be aftre update_vel since some state transitions look at velocity
        self.entity.animation.update(dt)#need to be after currentstate since animation will animate the current state -> i suupose it should be in update_physcis?

    def enter_state(self, newstate, **kwarg):
        self.entity.hitstop_states = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

class Stop(Idle):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.lifetime = kwarg.get('lifetime', 100)
        self.call_back = kwarg.get('call_back', None)
        self.original_velocity = self.entity.velocity.copy()

    def update(self, dt):
        self.entity.velocity = [0, 0]
        self.lifetime -= dt
        if self.lifetime < 0:
            self.entity.velocity = self.original_velocity.copy()
            if self.call_back: self.call_back()
            self.enter_state('Idle')

    def update_render(self, dt):#notmal, do nothing
        pass#no animation, no shader state, just stop
