import sys

class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.entity.state=str(type(self).__name__).lower()#the name of the class
        self.entity.animation.reset_timer()

    def update(self):
        self.update_state()

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update_state(self):
        pass

    def increase_phase(self):
        pass

class Once(Entity_States):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.duration=duration

    def update_state(self):
        self.duration-=1
        if self.duration<0:
            self.enter_state('Idle')

class Idle(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

class Opening(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=10

    def update_state(self):
        self.lifetime-=1
        self.open()

    def open(self):
        if self.lifetime<0:
            self.enter_state('Open')

class Open(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

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
