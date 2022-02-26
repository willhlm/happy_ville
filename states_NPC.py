import sys
from states_entity import Entity_States

class NPC_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        pass

    def update_state(self):
        pass

class Walk(NPC_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

class Idle(NPC_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
