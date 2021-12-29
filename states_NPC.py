import sys
from states_entity import Entity_States

class NPC_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

class Walk(NPC_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        pass

class Idle(Walk):
    def __init__(self,entity):
        super().__init__(entity)

    def horizontal_velocity(self):
        pass
