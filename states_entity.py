import constants as C

class Entity_States():
    def __init__(self,entity):
        self.entity = entity
        self.entity.state = str(type(self).__name__).lower()#the name of the class
        self.dir = self.entity.dir
        self.entity.animation.reset_timer()

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def increase_phase(self):
        pass

    def walk(self):
        self.entity.acceleration = C.acceleration.copy()
