import sys, random

class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.entity.state=str(type(self).__name__).lower()#the name of the class
        self.entity.animation.frame = 0

    def update(self):
        self.update_state()

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update_state(self):
        pass

    def increase_phase(self):
        pass

    def handle_input(self,input):
        pass

class Idle(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Invisible':
            self.enter_state('Invisible')
        elif input=='Hurt':
             self.enter_state('Hurt')
        elif input == 'Death':
             self.enter_state('Death')
        elif input == 'Opening':
            self.enter_state('Opening')
        elif input == 'Once':
            self.enter_state('Once')
        elif input =='Outline':
            self.enter_state('Outline')
        elif input == 'Transform':
            self.enter_state('Transform')

class Invisible(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if random.randint(0,500) == 1:
            self.enter_state('Idle')

class Once(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')

class Hurt(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Death':
            self.enter_state('Death')
        elif input=='Idle':
             self.enter_state('Idle')

class Death(Once):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.entity.kill()

class Opening(Once):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.entity.loots()
            self.enter_state('Interacted')

class Transform(Once):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
            self.enter_state('Interacted')

class Interacted(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

class Outline(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'Once':
            self.enter_state('Once')
