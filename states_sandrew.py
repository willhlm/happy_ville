import sys
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.2:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input=='Walk':
             self.enter_state('Walk')
        elif input =='Attack':
             self.enter_state('Attack_pre')
        elif input == 'Hurt':
            self.enter_state('Hurt')

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) <= 0.2:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input =='Attack':
             self.enter_state('Attack_pre')
        elif input == 'Hurt':
            self.enter_state('Hurt')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.dead()

class Hurt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')

class Stun(Enemy_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime = duration

    def update(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

class Attack_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Attack_main')

class Attack_main(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        hitbox = [self.entity.hitbox[2] + 30,self.entity.hitbox[3] + 30]
        self.attack_box = self.entity.attack(self.entity, size = hitbox, lifetime = 300, charge_blocks = True)
        self.entity.game_objects.eprojectiles.add(self.attack_box)

    def update(self):
        self.entity.velocity[0] += self.entity.dir[0] * 2
        self.attack_box.hitbox[0] = self.entity.hitbox[0]
        self.attack_box.hitbox[1] = self.entity.hitbox[1]

    def handle_input(self, input):
        if input == 'Wall':
            self.entity.velocity[0] = -5 * self.dir[0] * self.entity.velocity[0]
            self.increase_phase()
            self.entity.game_objects.camera_manager.camera_shake(duration = 15)
        elif input == 'sword':#if aila hits            
            self.entity.velocity[0] *= 3            
            self.entity.dir[0] *= -1

    def increase_phase(self):
        self.attack_box.kill()
        self.enter_state('Attack_post')

class Attack_post(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.AI.handle_input('Finish_attack')
