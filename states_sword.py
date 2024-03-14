import sys

def sign(num):
    if num > 0: return 1
    return -1

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.state = str(type(self).__name__).lower()#the name of the class
        self.entity.animation.reset_timer()

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished
        pass

    def handle_input(self,input):
        pass

    def update(self):#called every frame
        pass

class Slash_1(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.sign = sign(self.entity.dir[0])

    def update_hitbox(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] - self.sign * 28, self.entity.hitbox.center[1] - 14]

class Slash_2(Slash_1):
    def __init__(self,entity):
        super().__init__(entity)

class Slash_down(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        if self.entity.dir[0] > 0:
            self.offset = 45
        else:
            self.offset = 36

    def update_hitbox(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] + self.offset, self.entity.hitbox.center[1] - 4]

class Slash_up(Basic_states):#not implemented
    def __init__(self,entity):
        super().__init__(entity)
        if self.entity.dir[0] > 0:
            self.offset = 45
        else:
            self.offset = 36

    def update_hitbox(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] + self.offset, self.entity.hitbox.center[1] + 10]
