import sys
from states_entity import Entity_States

class Reindeer_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

    def handle_input(self,input):
        pass

    def update_state(self):
        pass

class Idle(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')

class Walk(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class Death(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Dead')

    def increase_phase(self):
        self.done=True

class Dead(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.entity.death()

    def update_state(self):
        pass

    def increase_phase(self):
        pass

class Transform(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.attack_distance=60
            self.enter_state('Transform_idle')

    def increase_phase(self):
        self.done=True

class Transform_idle(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Transform_walk')
        elif input =='Attack':
             self.enter_state('Attack')
        elif input =='Dash':
             self.enter_state('Dash')
        elif input =='Special_attack':
             self.enter_state('Special_attack')

class Transform_walk(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Transform_idle')
        elif input =='Attack':
             self.enter_state('Attack')
        elif input =='Dash':
             self.enter_state('Dash')
        elif input =='Special_attack':
             self.enter_state('Special_attack')

class Angry(Transform):#changing AI method
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera[-1].camera_shake(amp=3,duration=50)#amplitude, duration

class Stun(Reindeer_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

class Attack(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        self.done=False
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.attack.lifetime=10

    def update_state(self):
        if self.done:
            self.enter_state('Transform_idle')#idle

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            attack=self.entity.attack(self.entity)#make the object
            self.entity.projectiles.add(attack)#add to group but in main phase
        elif self.phase=='main':
            self.done=True

class Dash(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main','post']
        self.phase=self.phases[0]
        self.done=False#animation flag

    def update_state(self):
        self.entity.velocity[1]=0

        if self.phase == 'main':
            self.entity.velocity[0]=self.dir[0]*max(20,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            if self.entity.acceleration[0]==0:
                self.enter_state('Transform_idle')
            else:
                self.enter_state('Transform_walk')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            self.entity.velocity[0] = 30*self.dir[0]
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

class Special_attack(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        self.done=False
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.done:
            self.enter_state('Transform_idle')#idle

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            attack=self.entity.special_attack(self.entity)#make the object
            self.entity.projectiles.add(attack)#add to group but in main phase
        elif self.phase=='main':
            self.done=True
