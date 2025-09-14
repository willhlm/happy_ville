import sys
from gameplay.entities.states.states_entity import Entity_States

class Enemy_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def take_dmg(self, dmg):
        if self.entity.invincibile: return
        self.entity.health -= dmg

        if self.entity.health > 0:#check if dead¨
            self.entity.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period (minimum time needed to that the swrod doesn't hit every frame)
            self.entity.shader_state.handle_input('Hurt')#turn white
            self.entity.AI.handle_input('Hurt')
            self.handle_input('Hurt')#handle if we shoudl go to hurt state
            #self.game_objects.game.state_stack[-1].handle_input('dmg', duration = 15, amplitude = 10)#makes the game freez for few frames
            self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
        else:#if dead
            self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
            #self.game_objects.game.state_stack[-1].handle_input('dmg', duration = 15, amplitude = 30)#makes the game freez for few frames
            self.entity.aggro = False
            self.entity.invincibile = True
            self.entity.AI.deactivate()
            self.enter_state('Death')#overrite any state and go to deat
        return True#return truw to show that damage was taken        

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
        elif input == 'hide':
            self.enter_state('Hide_main')

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
        elif input == 'hide':
            self.enter_state('Hide_main')

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

class Hide_main(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Hide_post')

    def take_dmg(self, dmg):
        return True

class Hide_post(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='idle':
             self.enter_state('Idle')

    def take_dmg(self, dmg):
        return True

class Attack_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()#animation direction

    def increase_phase(self):
        self.enter_state('Attack_main')

class Attack_main(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.attack()

    def increase_phase(self):
        self.enter_state('Attack_post')

class Attack_post(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')
        self.entity.AI.handle_input('finish_attack')        
