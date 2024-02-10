import sys, math
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
        elif input == 'mix_colour':
            self.enter_state('Mix_colour')
        elif input == 'alpha':
            self.enter_state('Alpha')

class Hurt(Shader_states):#turn white
    def __init__(self,entity):
        super().__init__(entity)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.entity.shader = self.entity.game_objects.shaders['colour']
        self.next_animation = 'Idle'

    def draw(self):
        self.entity.shader['colour'] = (255,255,255,255)

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
        self.entity.shader['time']  = self.time#(colour,colour,colour)

class Mix_colour(Shader_states):#shade screen uses it
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['mix_colour']
        self.entity.shader['position'] = 0

    def draw(self):
        self.entity.shader['colour'] = self.entity.colour#higher alpha for lower parallax
        self.entity.shader['new_colour'] = self.entity.new_colour#higher alpha for lower parallax
        self.entity.shader['position'] = max((self.entity.game_objects.player.hitbox.centerx - self.entity.bounds.left)/self.entity.bounds[2],0)

    def handle_input(self,input):
        if input == 'idle':
            self.enter_state('Idle')

class Alpha(Shader_states):#fade screen uses it
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['alpha']
        self.alpha = 255

    def update(self):
        self.alpha *= 0.9
        if self.alpha < 5:
            self.entity.kill()

    def draw(self):
        self.entity.shader['alpha'] = self.alpha
