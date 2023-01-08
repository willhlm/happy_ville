import constants as C

class Entity_States():
    def __init__(self,entity):
        self.entity = entity
        self.state_name = str(type(self).__name__).lower()#the name of the class
        self.dir = self.entity.dir
        self.entity.animation.reset_timer()

    def update(self):
        self.update_state()

    def update_state(self):
        pass

    def walk(self):
        self.entity.acceleration = C.acceleration.copy()

    def stay_still(self):
        self.entity.acceleration = [0,C.acceleration[1]]

    def handle_input(self,input):
        pass

    def increase_phase(self):
        pass
