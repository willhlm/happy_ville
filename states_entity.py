class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.state_name=str(type(self).__name__).lower()#the name of the class
        self.dir=self.entity.dir
        self.entity.animation_stack[-1].reset_timer()

    def update(self):
        self.update_vel()
        self.update_state()

    def update_vel(self):
        self.entity.velocity[1]+=self.entity.acceleration[1]-self.entity.velocity[1]*self.entity.friction[1]#gravity
        self.entity.velocity[1]=min(self.entity.velocity[1],7)#set a y max speed

        self.entity.velocity[0]+=self.entity.dir[0]*self.entity.acceleration[0]-self.entity.friction[0]*self.entity.velocity[0]

    #    if self.entity.velocity[0]>0:
    #        self.entity.velocity[0]=min(self.entity.velocity[0],self.entity.max_vel)
    #    else:
    #        self.entity.velocity[0]=max(self.entity.velocity[0],-self.entity.max_vel)


    def update_state(self):
        pass

    def walk(self):
        self.entity.acceleration=[1,0.8]

    def stay_still(self):
        self.entity.acceleration=[0,0.8]

    def handle_input(self,input):
        pass
