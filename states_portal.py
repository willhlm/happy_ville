import sys

class Basic_states():
    def __init__(self,entity):
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
        self.entity.thickness = min(self.entity.thickness,0.2)              
        if self.entity.radius >= 0.1:
            self.enter_state('Idle')
        self.entity.radius = min(self.entity.radius,0.1)              

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'grow':
            self.enter_state('Grow')

class Grow(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):    
        self.entity.radius += self.entity.game_objects.game.dt*0.01    
        if self.entity.radius >= 1 - self.entity.thickness:
            self.enter_state('Idle')
        self.entity.radius = min(self.entity.radius, 1 - self.entity.thickness)       

class Shrink(Basic_states):#after beamtinf the challenge room
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):    
        self.entity.radius -= self.entity.game_objects.game.dt*0.005    
        if self.entity.radius <= self.entity.thickness:
            self.entity.thickness -= self.entity.game_objects.game.dt*0.005  
              
        if self.entity.radius or self.entity.thickness <= 0:
            self.entity.kill()    

        self.entity.radius = max(self.entity.radius, 0)       
        self.entity.thickness = max(self.entity.thickness, 0)       
