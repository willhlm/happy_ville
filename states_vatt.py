import sys
from states_entity import Entity_States
#from Entities import Vatt

class Vatt_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update(self):
        super().update()

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

    def change_state(self,input):
        self.enter_state(input)

class Idle(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        pass

    #    if not self.entity.collision_types['bottom']:
    #        self.enter_state('Fall_stand')

class Idle_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        pass

    def handle_input(self, input):
        self.change_state(input)
    #    if not self.entity.collision_types['bottom']:
    #        self.enter_state('Fall_stand')


class Walk(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        pass
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Run_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration = [1.9,0.8]

    def update_state(self):
        pass

    def handle_input(self, input):
        if input == str(type(self).__name__):
            pass
        else:
            self.change_state(input)
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Fall_stand(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.phases = ['pre','main']
        self.phase = pre

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def change_state(self,input):
        pass

class Death(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.loots()
            self.entity.kill()

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Hurt(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.aggro = True
            self.enter_state('Transform')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

    def handle_input(self, input):
        pass

class Hurt_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.counter = 0
            self.enter_state('Idle_aggro')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

    def handle_input(self, input):
        pass

class Transform(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done = False

    def update_state(self):
        pass

    def update_state(self):
        if self.done:
            self.enter_state('Idle_aggro')
            type(self.entity).aggro = True

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

    def handle_input(self, input):
        pass

class Stun(Vatt_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

    def change_state(self,input):
        pass

class Attack(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.attack.dir=self.dir#sword direction
        self.done=False
        self.phases=['pre','main']
        self.phase=self.phases[0]

        self.attack=self.entity.attack(self.entity)#make the ability object

    def update_state(self):
        if self.done:
            self.change_state('Idle')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            self.entity.projectiles.add(self.attack)#add sword to group but in main phase        elif self.phase=='main':
        elif self.phase=='main':
            self.done=True

class Javelin(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases = ['pre','main','post']
        self.phase = 'pre'
        self.entity.acceleration = [0,0]

    def update_state(self):

        if self.pahse == 'pre':
            self.entity.update_pos(self.entity)


    def change_state(self,input):
        pass

    def handle_input(self, input):
        pass
