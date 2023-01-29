import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        self.entity.reset_timer()

class Idle(Basic_states):
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
        elif input == 'Equip':
            self.enter_state('Equip')

class Equip(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'Idle':
            self.enter_state('Idle')

class Idle_once(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.kill()

class Invisible(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if random.randint(0,500) == 1:
            self.enter_state('Idle')

class Once(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Idle')

    def handle_input(self,input):
        if input == 'Death':
            self.enter_state('Death')

class Hurt(Basic_states):
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
        pass

    def increase_phase(self):
        self.entity.kill()

class Opening(Once):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.entity.loots()
        self.enter_state('Interacted')

class Transform(Once):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Interacted')

class Interacted(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

class Outline(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input=='Idle':
             self.enter_state('Idle')
        elif input == 'Once':
            self.enter_state('Once')

    def increase_phase(self):
        self.enter_state('Idle')

#for slash
class Slash_1(Idle_once):
    def __init__(self,entity):
        super().__init__(entity)

class Slash_2(Idle_once):
    def __init__(self,entity):
        super().__init__(entity)

class Slash_3(Idle_once):
    def __init__(self,entity):
        super().__init__(entity)

#for aila sword
class Level_1(Idle):
    def __init__(self,entity):
        super().__init__(entity)

class Level_2(Idle):
    def __init__(self,entity):
        super().__init__(entity)

class Level_3(Idle):
    def __init__(self,entity):
        super().__init__(entity)
