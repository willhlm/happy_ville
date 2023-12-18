import sys
import constants as C

class Shader_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.shader_state = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def update(self):#called in update loop
        pass

    def draw(self):#called just before draw
        pass

class Idle(Shader_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['idle']

    def handle_input(self,input):
        if input == 'Hurt':
            self.enter_state('Hurt')

class Hurt(Shader_states):#turn white
    def __init__(self,entity):
        super().__init__(entity)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.entity.shader = self.entity.game_objects.shaders['hurt']
        self.next_animation = 'Idle'

    def update(self):
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion
        if self.duration < 0:
            self.enter_state(self.next_animation)

    def handle_input(self,input):
        if input == 'Invincibile':
            self.next_animation = 'Invincibile'

class Invincibile(Shader_states):#blink white
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['invincible']
        self.duration = C.invincibility_time_player-(C.hurt_animation_length+1)#a duration which considers the player invinsibility
        self.time = 0

    def update(self):
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion
        self.time += 0.5 * self.entity.game_objects.game.dt*self.entity.slow_motion

        if self.duration < 0:
            self.enter_state('Idle')

    def draw(self):
        self.entity.shader['time'] = self.time
