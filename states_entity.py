class Entity_States():
    def __init__(self,entity):
        self.entity = entity
        self.entity.state = type(self).__name__.lower()#the name of the class
        self.dir = self.entity.dir.copy()
        self.entity.animation.reset_timer()

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def increase_phase(self):
        pass
