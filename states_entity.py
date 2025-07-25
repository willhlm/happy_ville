class Entity_States():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        self.dir = self.entity.dir.copy()

    def update(self):
        pass

    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass
