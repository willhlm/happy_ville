class Entity_States():
    def __init__(self,entity):
        self.entity=entity
        self.state_name=str(type(self).__name__).lower()#the name of the class
        self.dir=self.entity.dir
        self.entity.animation_stack[-1].reset_timer()

    def update(self):
        self.update_state()

    def update_state(self):
        pass

    def walk(self):
        self.entity.acceleration=[1,0.7]

    def stay_still(self):
        self.entity.acceleration=[0,0.7]

    def handle_input(self,input):
        pass
