class Entity_states():
    def __init__(self,entity):
        self.entity=entity
        self.dir=self.entity.dir
        self.framerate=4
        self.frame=0

    def update(self):
        self.update_vel()
        self.update_state()

    def update_vel(self):
        self.entity.velocity[1]=self.entity.velocity[1]+self.entity.acceleration[1]-self.entity.velocity[1]*self.entity.friction[1]#gravity
        self.entity.velocity[1]=min(self.entity.velocity[1],7)#set a y max speed

        self.horizontal_velocity()#some states stay still
        self.entity.velocity[0]=self.entity.velocity[0]-self.entity.friction[0]*self.entity.velocity[0]#friction

    def horizontal_velocity(self):
        self.entity.velocity[0]+=self.dir[0]*self.entity.acceleration[0]
        self.entity.velocity[0]=self.dir[0]*min(abs(self.entity.velocity[0]),self.entity.max_vel)#max horizontal speed

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys
        self.reset_timer()

    def update_animation(self):
        statename=str(type(self).__name__)

        self.entity.image = self.entity.sprites.get_image(statename,self.frame//self.framerate,self.dir,self.phase)
        self.frame += 1

        if self.frame == self.entity.sprites.get_frame_number(statename,self.dir,self.phase)*self.framerate:
            self.reset_timer()

    def reset_timer(self):
        self.frame=0

class Walk(Entity_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        pass

class Idle(Walk):
    def __init__(self,entity):
        super().__init__(entity)

    def horizontal_velocity(self):
        pass
