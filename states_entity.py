class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.state_name=str(type(self).__name__)#the name of the class
        self.dir=self.entity.dir
        self.framerate=4
        self.frame=0

    def update(self):
        self.update_vel()
        self.update_state()

    def update_vel(self):
        self.entity.velocity[1]=self.entity.velocity[1]+self.entity.acceleration[1]-self.entity.velocity[1]*self.entity.friction[1]#gravity
        self.entity.velocity[1]=min(self.entity.velocity[1],7)#set a y max speed

        self.entity.velocity[0]+=self.dir[0]*self.entity.acceleration[0]

#        if self.entity.velocity[0]<0:
    #        self.entity.velocity[0]=max(self.entity.velocity[0],-self.entity.max_vel)
        #else:
        #    self.entity.velocity[0]=min(self.entity.velocity[0],self.entity.max_vel)

        #self.entity.velocity[0]=self.dir[0]*min(abs(self.entity.velocity[0]),self.entity.max_vel)#max horizontal speed
        self.entity.velocity[0]=self.entity.velocity[0]-self.entity.friction[0]*self.entity.velocity[0]#friction

    def walk(self):
        self.entity.acceleration=[1,0.8]

    def stay_still(self):
        self.entity.acceleration=[0,0.8]

    def reset_timer(self):
        self.frame=0

    def update_animation(self):
        self.entity.image = self.entity.sprites.get_image(self.state_name,self.frame//self.framerate,self.dir,self.phase)
        self.frame += 1

        if self.frame == self.entity.sprites.get_frame_number(self.state_name,self.dir,self.phase)*self.framerate:
            self.reset_timer()
            self.increase_phase()
