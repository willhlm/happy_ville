import sys, random
from states_entity import Entity_States

class Basic_states():
    def __init__(self,entity,next_colour):
        self.entity = entity
        self.state_name = str(type(self).__name__).lower()#the name of the class
        self.next_colour = next_colour

    def update(self):
        pass

    def enter_state(self,newstate, next_colour = None):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,next_colour)#make a class based on the name of the newstate: need to import sys

class Idle(Basic_states):
    def __init__(self,entity,next_colour):
        super().__init__(entity,next_colour)

class Turn(Basic_states):#smoothlyc hange colour
    def __init__(self,entity,next_colour):
        super().__init__(entity,next_colour)
        self.sign = []
        for colour_code in range(3):
            if self.entity.colour[colour_code] - next_colour[colour_code] > 0:#determine which way to change the colur
                self.sign.append(-1)
            else:
                self.sign.append(1)

    def update(self):
        temp_colour = []
        for index, colour in enumerate(self.entity.colour[:3]):
            colour = colour + self.sign[index]
            temp_colour.append(colour)
        temp_colour.append(self.entity.colour[-1])

        self.entity.image.fill(temp_colour)
        self.entity.colour = temp_colour

        if self.entity.colour[:3] == self.next_colour[:3]:
            self.enter_state('Idle')
