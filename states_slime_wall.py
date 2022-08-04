import sys

class Enemy_states():
    def __init__(self,entity):
        self.entity=entity
        self.state_name=str(type(self).__name__).lower()#the name of the class
        self.dir=self.entity.dir
        self.entity.animation_stack[-1].reset_timer()
        self.phase='main'

    def update(self):
        self.update_state()

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def update_state(self):
        pass

    def walk(self):
        self.entity.acceleration=[1,0.7]

    def stay_still(self):
        self.entity.acceleration=[0,0]

    def increase_phase(self):
        pass

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input =='Attack':
             self.enter_state('Attack')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        #self.entity.velocity[1]=-self.entity.dir[1]
        self.entity.velocity[0]=self.entity.dir[0]

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.loots()
            self.entity.death()

    def increase_phase(self):
        self.done=True

class Hurt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

class Stun(Enemy_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime = duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')
