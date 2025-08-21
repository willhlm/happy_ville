import sys
import constants as C

def sign(num):
    if num > 0: return 1
    return -1

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
        self.entity.hitbox[2] = 45
        self.entity.hitbox[3] = 29
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
        self.entity.hitbox[2] = 40
        self.entity.hitbox[3] = 35                        
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
        self.entity.hitbox[2] = 40
        self.entity.hitbox[3] = 35
        self.entity.dir = [sign(self.entity.dir[0]), -1]#sword dir

        if self.entity.dir[0] > 0:
            self.offset = 45
        else:
            self.offset = 36

    def update_rect(self):
        self.entity.rect.center = [self.entity.hitbox.center[0] + self.offset, self.entity.hitbox.center[1] - 4]

    def sword_jump(self):
        self.entity.entity.velocity[1] = C.pogo_vel

#states for the stones (the stones alters the sword properties)
class Stone_states():
    def __init__(self, entity):
        self.entity = entity    

    def enter_state(self, newstate, key, **kwarg):
        self.entity.stone_states[key] = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def projectile_collision(self, eprojectile):#called when projectile collision
        eprojectile.take_dmg(self.entity.dmg)

    def enemy_collision(self):#called when wnemy collision
        pass

    def slash_speed(self):#called whenever sing the sword
        pass

class Enemy_collision(Stone_states):#blue stone can set this satte
    def __init__(self,entity):
        super().__init__(entity)

    def enemy_collision(self):
        self.entity.entity.add_spirit()        

class Projectile_collision(Stone_states):#pirpöle stone ca nset this state
    def __init__(self, entity):
        super().__init__(entity)

    def projectile_collision(self, eprojecitile):
        eprojecitile.reflect(self.entity.dir, self.entity.hitbox.center)
        self.entity.sword_jump()        

class Slash(Stone_states):#green stone can set this
    def __init__(self, entity):
        super().__init__(entity)

    def slash_speed(self):#called whenever sing the sword
        self.entity.entity.animation.framerate = 0.33 #the frame rate is set back when the player exits the sword state
