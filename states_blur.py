import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input,**kwarg):
        pass

#for zoom stuff
class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = None        

    def set_uniform(self):
        pass

class Blur(Basic_states):#live blur
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['blur']

    def set_uniform(self):
        self.entity.shader['blurRadius'] = self.entity.blur_radius