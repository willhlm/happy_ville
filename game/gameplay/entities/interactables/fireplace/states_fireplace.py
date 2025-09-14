import sys, random
from gameplay.entities.states.states_entity import Entity_States

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
        if input == 'Interact':
            self.enter_state('Interact')

    def set_animation_name(self,name):#called for UI abilities
        self.entity.state = name
        self.entity.animation.frame = 0

class Interact(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.make_light()
        self.entity.channel = self.entity.game_objects.sound.play_sfx(self.entity.sounds['idle'][0], loop = -1, vol = 0.3)

    def increase_phase(self):
        self.enter_state('Interacted')

class Interacted(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input):#fire place
        if input == 'Interact':
            self.enter_state('Pre_idle')

class Pre_idle(Basic_states):#fire palce
    def __init__(self,entity):
        super().__init__(entity)
        for light in self.entity.light_sources:
            self.entity.game_objects.lights.remove_light(light)
        self.entity.light_sources = []   
        self.entity.channel.fadeout(400) 

    def increase_phase(self):
        self.enter_state('Idle')
