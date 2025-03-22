import sys, math, entities

class Reindeer_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.state = type(self).__name__.lower()#the name of the class
        self.dir = self.entity.dir.copy()
        self.entity.animation.reset_timer()

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate.capitalize())(self.entity)#make a class based on the name of the newstate: need to import sys

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def increase_phase(self):
        pass

class Idle_nice(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.01:
            self.enter_state('Walk')

class Walk_nice(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) < 0.01:
            self.enter_state('Idle')

class Transform(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Idle')

class Idle(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) > 0.01:
            self.enter_state('Walk')

    def handle_input(self,input):
        if input =='attack':
             self.enter_state('Attack_pre')
        elif input =='charge':
             self.enter_state('charge_pre')

class Walk(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if abs(self.entity.velocity[0]) < 0.01:
            self.enter_state('idle')

    def handle_input(self,input):
        if input =='attack':
             self.enter_state('Attack_pre')
        elif input =='charge':
             self.enter_state('charge_pre')
        elif input =='Jump':
             self.enter_state('Jump_pre')

class Roar_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Roar_main')

class Roar_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera_manager.camera_shake(amp = 3, duration = 100)#amplitude, duration
        self.cycles = 4

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles == 0: self.enter_state('Roar_post')        

class Roar_post(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')        

class Death(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Dead')

class Dead(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.dead()

    def update(self):
        self.entity.velocity = [0,0]

class Attack_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
         self.enter_state('Attack_main')

class Attack_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        attack = self.entity.attack(self.entity, lifetime = 10)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.entity.AI.state.animation_finish()
        self.enter_state('idle')

class Charge_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)   
        self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)     

    def increase_phase(self):
        self.enter_state('charge_main')   

class Charge_main(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)        
        self.cycles = 3       

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles == 0: self.enter_state('charge_run')                     

class Charge_run(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.cycles = 1#to add a delay from running to attack
        self.next = False#to add a delay from running to attack

    def update(self):
        self.entity.velocity[0] = self.entity.dir[0] * 5
        if abs(self.entity.AI.player_distance[0]) < self.entity.attack_distance[0]:    
            self.next = True

    def increase_phase(self):
        if not self.next: return
        self.cycles -= 1 
        if self.cycles == 0: self.enter_state('charge_attack_pre')                   

class Charge_attack_pre(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('charge_attack')   

class Charge_attack(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)
        attack = self.entity.attack(self.entity, lifetime = 10)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.enter_state('charge_post')           

class Charge_post(Reindeer_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.AI.state.animation_finish()
        self.enter_state('idle')            