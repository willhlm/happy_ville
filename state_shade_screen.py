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
        self.change_vel = 2#the speed to change the colour
        for colour_code in range(3):
            if self.entity.colour[colour_code] - next_colour[colour_code] > 0:#determine which way to change the colur
                self.sign.append(-1)
            else:
                self.sign.append(1)

    def update(self):
        temp_colour = []
        for index, colour in enumerate(self.entity.colour[:3]):
            colour = colour + self.sign[index]*self.change_vel*self.entity.game_objects.game.dt
            temp_colour.append(int(colour))
        temp_colour.append(self.entity.colour[-1])#append the alpha value

        self.entity.image.fill(temp_colour)
        self.entity.colour = temp_colour#update the colour
        self.finish()

    def finish(self):#if the difference for all 3 colour code are smaller than 3, go to idle
        for colour_code in range(3):
            if abs(self.entity.colour[colour_code] - self.next_colour[colour_code]) < self.change_vel + 1:
                self.sign[colour_code] = 0
            else: return
        self.enter_state('Idle')
