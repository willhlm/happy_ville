import sys
from gameplay.entities.states.states_entity import Entity_States

class NPC_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Walk(NPC_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)

class Idle(NPC_states):
    def __init__(self,entity):
        super().__init__(entity)
