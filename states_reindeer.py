import sys
from states_entity import Entity_States

class Reindeer_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

    def update(self):
        self.update_state()

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

    def increase_phase(self):
        self.enter_state('Dead')

class Dead(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.entity.dead()

    def update_state(self):
        pass

    def increase_phase(self):
        pass

class Transform(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.entity.attack_distance=60
        self.enter_state('Transform_idle')

class Transform_idle(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Transform_walk')
        elif input =='Attack':
             self.enter_state('Attack_pre')
        elif input =='Dash':
             self.enter_state('Dash_pre')
        elif input =='Special_attack':
             self.enter_state('Special_attack')
        elif input =='Jump':
             self.enter_state('Jump_pre')

class Rest(Reindeer_states):#enters here after attakes to "rest"
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def increase_phase(self):
        self.enter_state('Transform_idle')

class Transform_walk(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Transform_idle')
        elif input =='Attack':
             self.enter_state('Attack_pre')
        elif input =='Dash':
             self.enter_state('Dash_pre')
        elif input =='Special_attack':
             self.enter_state('Special_attack_pre')
        elif input =='Jump':
             self.enter_state('Jump_pre')

class Angry(Transform):#changing AI method
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.camera_shake(amp=3,duration=50)#amplitude, duration

class Jump_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction

    def increase_phase(self):
         self.enter_state('Jump_main')

class Jump_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.velocity = [10*self.dir[0],-10]

    def update_state(self):
        if self.entity.velocity[1]>0.7:
            self.enter_state('Fall_pre')

class Fall_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction

    def increase_phase(self):
         self.enter_state('Fall_main')

class Fall_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction

    def handle_input(self,input):
        if input == 'Ground':
            self.enter_state('Fall_post')

class Fall_post(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction

    def increase_phase(self):
         self.enter_state('Transform_walk')
         self.entity.AI.finish_action()

class Stun(Reindeer_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

class Attack_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        self.stay_still()

    def increase_phase(self):
         self.enter_state('Attack_main')

class Attack_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.attack.lifetime=10
        attack=self.entity.attack(self.entity)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.enter_state('Transform_idle')
        self.entity.AI.finish_action()

class Dash_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.dir=self.entity.dir.copy()

    def increase_phase(self):
         self.enter_state('Dash_main')

class Dash_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.dir=self.entity.dir.copy()
        self.entity.velocity[0] = 30*self.dir[0]

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(20,abs(self.entity.velocity[0]))#max horizontal speed

    def increase_phase(self):
         self.enter_state('Dash_post')

class Dash_post(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.dir=self.entity.dir.copy()

    def increase_phase(self):
        self.rest(duration = 50)

class Special_attack_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction

    def increase_phase(self):
        self.enter_state('Special_attack_main')

class Special_attack_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        attack=self.entity.special_attack(self.entity)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.rest(duration = 50)
