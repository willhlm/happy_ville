import sys, math, random

class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.entity.state=str(type(self).__name__).lower()#the name of the class
        self.entity.animation.reset_timer()

    def update(self):
        self.update_state()

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update_state(self):
        pass

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class Idle(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.time=0

    def update_state(self):
        self.time+=1
        self.entity.speed()

        rand=random.randint(0, 100)
        if rand==1:
            self.enter_state('Flip')

class Once(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.flag = False#to make sure it doesn't finish in the first frame = 0

    def update_state(self):
        if self.entity.animation.frame==0 and self.flag:#enter when animation is finished
            self.finish()

        self.flag = True

    def finish(self):
        self.enter_state('Idle')

class Flip(Once):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1]=self.entity.velocity[1]*0.8
        self.entity.velocity[0]=self.entity.velocity[0]*0.8

    def update_state(self):
        super().update_state()
