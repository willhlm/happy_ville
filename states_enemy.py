import sys
from states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

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
            self.phase='pre'

    def change_state(self,input):
        self.enter_state(input)

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        pass
    #    if not self.entity.collision_types['bottom']:
    #        self.enter_state('Fall_stand')


class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand')


class Jump_run(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

        self.entity.velocity[1] = -11
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_run')

    def change_state(self,input):
        pass

class Jump_stand(Jump_run):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_stand')

    def change_state(self,input):
        pass

class Fall_run(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Walk')
    #    elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
    #        self.enter_state('Wall')

    def change_state(self,input):
        pass

class Fall_stand(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def change_state(self,input):
        pass

class Wall(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.friction[1]=0.4

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.entity.friction[1]=0
            self.enter_state('Idle')

        elif not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction[1]=0
            self.enter_state('Fall_run')

    def change_state(self,input):
        pass

class Dash(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main','post']
        self.phase=self.phases[0]
        self.entity.spirit -= 10
        self.done=False#animation flag
        self.walking()#check if we were walking are idle before dash
        self.entity.velocity[0] = 30*self.dir[0]

    def walking(self):
        if abs(self.entity.velocity[0])>0.5:
            self.walk=True
        else:
            self.walk=False

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            if self.walk:
                self.enter_state('Walk')
            else:
                self.enter_state('Idle')

        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.enter_state('Wall')

    def change_state(self,input):
        pass

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.phase='main'
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.loots()
            self.entity.kill()

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Hurt(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.phase='main'
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass


class Trans(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        pass

    def change_state(self,input):
        pass

class Stun(Enemy_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

    def change_state(self,input):
        pass
