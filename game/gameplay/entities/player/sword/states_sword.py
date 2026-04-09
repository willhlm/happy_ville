import sys
from engine import constants as C
from engine.utils.functions import sign

class Basic_states():#states for aila sword
    def __init__(self, entity):
        self.entity = entity
        self.entity.animation.play(str(type(self).__name__).lower())#the name of the class

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished
        pass

    def handle_input(self,input):
        pass

    def update(self, dt):
        pass

    def update_rect(self):
        pass

    def sword_jump(self):
        pass

class Slash_1(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.sign = sign(self.entity.dir[0])
        self.entity.lifetime = 10#swrod hitbox duration
        self.entity.apply_hitbox_size(45, 29)
        self.entity.dir = [self.sign, 0]#sword dir

    def update_rect(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] - self.sign * 35, self.entity.hitbox.center[1] - 14]

class Slash_2(Slash_1):
    def __init__(self,entity):
        super().__init__(entity)

class Slash_up(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.lifetime = 10#swrod hitbox duration
        self.entity.apply_hitbox_size(40, 35)
        self.entity.dir = [sign(self.entity.dir[0]), 1]#sword dir

        if self.entity.dir[0] > 0:
            self.offset = 45
        else:
            self.offset = 36

    def update_rect(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] + self.offset, self.entity.hitbox.center[1] + 10]

class Slash_down(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.lifetime = 10#swrod hitbox duration
        self.entity.apply_hitbox_size(40, 35)
        self.entity.dir = [sign(self.entity.dir[0]), -1]#sword dir

        if self.entity.dir[0] > 0:
            self.offset = 45
        else:
            self.offset = 36

    def update_rect(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] + self.offset, self.entity.hitbox.center[1] - 4]

    def sword_jump(self):
        self.entity.entity.velocity[1] = C.pogo_vel
