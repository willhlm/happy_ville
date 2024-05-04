import sys, states

class Basic_states():
    def __init__(self, entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        pass

    def handle_input(self,input):
        pass

class Spawn(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)   

    def update(self):
        self.entity.radius += self.entity.game_objects.game.dt*0.001    
        self.entity.thickness += 2*self.entity.game_objects.game.dt*0.001   
        self.entity.thickness = min(self.entity.thickness,0.1)              
        if self.entity.radius >= 0.1:
            self.enter_state('Idle')
        self.entity.radius = min(self.entity.radius,0.1)              

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'grow':
            self.enter_state('Grow')
        elif input == 'shrink':
            self.enter_state('Shrink')

class Grow(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):    
        self.entity.radius += self.entity.game_objects.game.dt*0.01    
        if self.entity.radius >= 1 - self.entity.thickness:
            self.enter_state('Idle')
            new_state = states.Challenge_rooms(self.entity.game_objects.game, self.entity, 'Room_' + str(self.entity.ID))
            new_state.enter_state()
        self.entity.radius = min(self.entity.radius, 1 - self.entity.thickness)       

class Shrink(Basic_states):#after beamting the challenge room
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):    
        self.entity.radius -= self.entity.game_objects.game.dt*0.005    
        if self.entity.radius <= self.entity.thickness:
            self.entity.thickness -= self.entity.game_objects.game.dt*0.005  
              
        if self.entity.radius <= 0 or self.entity.thickness <= 0:
            self.entity.kill()    
            return    
