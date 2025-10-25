import sys, random

class Vatt_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        #self.dir = self.entity.dir.copy()

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self, dt):
        pass
    
    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

    def modify_hit(self, effect):
        return effect

class Idle(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        if abs(self.entity.velocity[0]) > 0.2:
            self.enter_state('Run')        
        elif not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_pre')

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Run':
            self.enter_state('Run')
        elif input == 'Walk':
            self.entity.dir[0] = random.choice((1,-1))
            self.enter_state('Walk')
        elif input == 'Transform':
            self.enter_state('Transform')

class Idle_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity = [0,0]

    def update(self, dt):
        if abs(self.entity.velocity[0]) > 0.2:
            self.enter_state('Run_aggro')        
        elif not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_aggro_pre')

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt_aggro')
        elif input == 'Run':
            self.enter_state('Run_aggro')
        elif input == 'Attack':
            self.enter_state('Javelin_pre')
            
class Walk(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Idle':
            self.enter_state('Idle')
        elif input == 'Transform':
            self.enter_state('Transform')

class Fall_stand_pre(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self, input):
        if input=='Hurt':
            self.enter_state('Hurt')
        elif input == 'Transform':
            self.enter_state('Transform')
        elif input == 'Ground':
            self.enter_state('Idle')

class Fall_stand_main(Fall_stand_pre):
    def __init__(self,entity):
        super().__init__(entity)

class Fall_stand_aggro_pre(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self, input):
        if input=='Hurt':
            self.enter_state('Hurt_aggro')
        elif input == 'Ground':
            self.enter_state('Idle_aggro')
        
    def increase_phase(self):
        self.enter_state('Fall_stand_aggro_main')

class Fall_stand_aggro_main(Fall_stand_aggro_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        pass

class Run(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        if abs(self.entity.velocity[0]) < 0.2:
            self.enter_state('Idle')

    def handle_input(self, input):
        if input == 'Run':
            pass
        elif input == 'Transform':
            self.enter_state('Transform')

class Run_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
        if abs(self.entity.velocity[0]) < 0.2:
            self.enter_state('Idle_aggro')

    def handle_input(self, input):
        if input == 'Run':
            pass
        elif input == 'Attack':
            self.enter_state('Javelin_pre')

class Death(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.velocity = [0, 0]

    def increase_phase(self):
        self.entity.dead()

class Hurt(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Transform')

class Hurt_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle_aggro')

class Transform(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)        

    def increase_phase(self):
        self.enter_state('Idle_aggro')
        self.entity.AI.handle_input('Aggro')
        if not self.entity.flags['aggro']:#so that only one vatt calls turn clan
            self.entity.turn_clan()

class Stun(Vatt_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.lifetime = duration

    def update(self, dt):
        self.lifetime-= dt
        if self.lifetime<0:
            self.enter_state('Idle')

class Javelin_pre(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)        
        self.counter = 0
        self.pre_pos_increment = [-3,-2,-1,-1,-1,-1]

    def update(self, dt):
        self.entity.velocity = [0,0]
        self.counter += dt
        if int(self.counter/4) >= len(self.pre_pos_increment):
            pass
        elif self.counter%4 == 0:
            self.entity.velocity[1] = self.pre_pos_increment[int(self.counter/4)]

    def increase_phase(self):
        self.enter_state('Javelin_main')

class Javelin_main(Javelin_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()

    def update(self, dt):
        self.entity.velocity = [3.5* self.dir[0],0]
        self.counter += dt
        if self.counter > 24:
            self.enter_state('Javelin_post')

    def increase_phase(self):
        pass

class Javelin_post(Javelin_pre):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def update(self, dt):
        pass

    def increase_phase(self):
        self.enter_state('Fall_stand_aggro_pre')
        self.entity.AI.handle_input('Finish_attack')
