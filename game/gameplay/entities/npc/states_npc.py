import sys

class NPC_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        #self.dir = self.entity.dir.copy()

    def update(self, dt):
        pass
    
    def handle_input(self, input):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

class Walk(NPC_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)

class Idle(NPC_states):
    def __init__(self,entity):
        super().__init__(entity)
