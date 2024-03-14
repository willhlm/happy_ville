import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished
        pass

    def handle_input(self,input):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input,**kwarg):
        if input == 'Once':
            self.enter_state('Once',**kwarg)
        elif input == 'Death':
             self.enter_state('Death')
        elif input == 'Invisible':
            self.enter_state('Invisible')
        elif input == 'Opening':
            self.enter_state('Opening')
        elif input =='Outline':
            self.enter_state('Outline')
        elif input == 'Transform':
            self.enter_state('Transform')
        elif input == 'Interact':
            self.enter_state('Interact')

    def set_animation_name(self,name):#called for UI abilities
        self.entity.state = name
        self.entity.animation.frame = 0

class Death(Basic_states):#idle once
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.invincibile = True

    def increase_phase(self):
        self.entity.kill()

class Once(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.next_state = kwarg['next_state']
        self.entity.state = kwarg['animation_name']

    def increase_phase(self):
        self.enter_state(self.next_state)

#special ones
class Outline(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input,**kwarg):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'Once':
            self.enter_state('Once',**kwarg)

    def increase_phase(self):
        self.enter_state('Idle')

class Invisible(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if random.randint(0,500) == 1:
            self.enter_state('Idle')

class Opening(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.loots()
        self.enter_state('Interacted')

class Transform(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Interacted')

class Interact(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Interacted')

class Interacted(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
