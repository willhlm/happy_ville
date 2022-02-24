import sys

class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.framerate=4
        self.frame=0

    def update(self):
        self.update_state()

    def reset_timer(self):
        self.frame=0

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update_animation(self, frame_rate = 4):
        statename=str(type(self).__name__)

        self.entity.image = self.entity.sprites[statename][self.frame//frame_rate]
        self.frame += 1

        if self.frame == len(self.entity.sprites[statename])*frame_rate:
            self.reset_timer()

class Fall(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.entity.speed()

    def change_state(self):
        self.enter_state('Death')

class Death(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=10
        self.entity.velocity=[0,0]

    def update_state(self):        
        self.lifetime-=1
        self.destroy()

    def destroy(self):
        if self.lifetime<0:
            statename=str(type(self.entity).__name__)
            self.entity.create_particles(statename,1)
            self.entity.kill()

    def change_state(self):
        pass
