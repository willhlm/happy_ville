import sys, random
from states_entity import Entity_States

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.state_name = str(type(self).__name__).lower()#the name of the class

    def update(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def set_colour(self,new_colour):
        pass

    def handle_input(self,input):
        if input == 'Turn':
            self.enter_state('Turn')

class Turn(Basic_states):#smoothlyc hange colour
    def __init__(self,entity):
        super().__init__(entity)

    def set_colour(self,new_colour):
        temp_colour = []
        for colour in self.entity.colour[:3]:
            colour -= 1
            temp_colour.append(colour)
        temp_colour.append(self.entity.colour[-1])

        self.entity.image.fill(temp_colour)
        self.entity.colour = temp_colour
        if self.entity.colour[:3] == new_colour[:3]:
            self.enter_state('Turnd')

    def handle_input(self,input):
        if input == 'Idle':
            self.enter_state('Turn_back')

class Turn_back(Basic_states):#smoothlyc hange colour
    def __init__(self,entity):
        super().__init__(entity)

    def set_colour(self,new_colour):
        temp_colour = []
        for colour in self.entity.colour[:3]:
            colour += 1
            temp_colour.append(colour)
        temp_colour.append(self.entity.colour[-1])

        self.entity.image.fill(temp_colour)
        self.entity.colour = temp_colour

        if self.entity.colour[:3] == new_colour[:3]:
            self.enter_state('Idle')

    def handle_input(self,input):
        if input == 'Turn':
            self.enter_state('Turn')

class Turnd(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def set_colour(self,new_colour):
        pass

    def handle_input(self,input):
        if input == 'Idle':
            self.enter_state('Turn_back')
