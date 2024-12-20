import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.state = type(self).__name__.lower()#the name of the class
        self.entity.animation.reset_timer()

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

class A_idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'press':
            self.enter_state('A_select')

class A_select(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('A_press')

class A_press(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('A_idle')

class B_idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'press':
            self.enter_state('B_select')

class B_select(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('B_press')

class B_press(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('B_idle')

class Lb_idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'press':
            self.enter_state('Lb_select')

class Lb_select(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Lb_press')

class Lb_press(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('Lb_idle')

class Rb_idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'press':
            self.enter_state('Rb_select')

class Rb_select(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Rb_press')

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('Rb_idle')

class Rb_press(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):
        if input == 'release':
            self.enter_state('Rb_idle')
