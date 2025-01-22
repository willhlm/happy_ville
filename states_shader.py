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
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['idle']

    def handle_input(self, input, **kwarg):
        if input == 'Hurt':
            self.enter_state('Hurt', **kwarg)
        elif input == 'mix_colour':
            self.enter_state('Mix_colour')
        elif input == 'alpha':
            self.enter_state('Alpha')
        elif input == 'tint':
            self.enter_state('Tint', **kwarg)
        elif input == 'blur':
            self.enter_state('Blur')

class Hurt(Shader_states):#turn white and shake it a bit -> enteties use it
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.entity.shader = self.entity.game_objects.shaders['shock_damage']
        self.next_animation = 'Idle'
        self.time = 0
        self.amplitude = kwarg.get('amplitude', 1) * 0.05
        self.frequency = kwarg.get('frequency', 100)
        self.colour = kwarg.get('colour', [1, 1, 1, 1])
        self.decay_rate = kwarg.get('decay_rate', 10)
        self.direction = kwarg.get('direction', [1,0])

    def draw(self):
        self.entity.shader['time'] = self.time*0.01
        self.entity.shader['frequency'] = self.frequency
        self.entity.shader['amplitude'] = self.amplitude
        self.entity.shader['colour'] = self.colour
        self.entity.shader['decay_rate'] = self.decay_rate
        self.entity.shader['direction'] = self.direction


    def update(self):
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion
        self.time += self.entity.game_objects.game.dt*self.entity.slow_motion
        if self.duration < 0:
            self.enter_state(self.next_animation)

    def handle_input(self,input,**kwarg):
        if input == 'Invincibile':
            self.next_animation = 'Invincibile'

class Invincibile(Shader_states):#blink white -> enteyties use it
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['invincible']
        self.duration = C.invincibility_time_player - (C.hurt_animation_length + 1)#a duration which considers the player invinsibility
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

class Teleport(Shader_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 0
        self.entity.shader = entity.game_objects.shaders['teleport']#apply teleport first and then bloom

    def update(self):
        self.time += 0.01
        if self.time >= 1:
            self.entity.kill()

    def draw(self):
        self.entity.shader['progress'] = self.time

class Glow(Shader_states):#tint with a colour and apply bloom
    def __init__(self,entity, colour = [100,200,255,100]):
        super().__init__(entity)
        self.colour = colour
        self.entity.shader = self.entity.game_objects.shaders['bloom']
        self.layer1 = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#!! need to move it somewehre in memory

    def draw(self):
        self.entity.game_objects.shaders['tint']['colour'] = self.colour
        self.entity.game_objects.game.display.render(self.entity.image, self.layer1, shader = self.entity.game_objects.shaders['tint'])#shader render
        self.entity.image = self.layer1.texture

class Shining(Shader_states):#called for aila when particle hit when guide dissolves
    def __init__(self,entity, colour = [0.39, 0.78, 1,1]):
        super().__init__(entity)
        self.colour = colour
        self.entity.shader = self.entity.game_objects.shaders['shining']
        self.layer1 = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#make a layer ("surface")
        self.time = 0
        self.speed = 0.6

    def update(self):
        self.time += self.entity.game_objects.game.dt*0.01

    def draw(self):
        self.entity.shader['TIME'] = self.time
        self.entity.shader['tint'] = self.colour
        self.entity.shader['speed'] = self.speed

class Dissolve(Shader_states):#disolve and bloom
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.noise_layer = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks
        self.empty = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks
        self.entity.shader = self.entity.game_objects.shaders['bloom']

        self.time = 0
        self.colour = kwarg.get('colour', [1,0,0,1])
        self.size = kwarg.get('size', 0.1)

    def update(self):
        self.time += self.entity.game_objects.game.dt*0.01

    def draw(self):
        self.empty.clear(0,0,0,0)
        self.entity.game_objects.shaders['noise_perlin']['u_resolution'] = self.entity.image.size
        self.entity.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.entity.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.entity.game_objects.shaders['noise_perlin']['scale'] = [10,10]#"standard"
        self.entity.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader = self.entity.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.entity.game_objects.shaders['dissolve']['dissolve_texture'] = self.noise_layer.texture
        self.entity.game_objects.shaders['dissolve']['dissolve_value'] = max(1 - self.time,0)
        self.entity.game_objects.shaders['dissolve']['burn_color'] = self.colour
        self.entity.game_objects.shaders['dissolve']['burn_size'] = self.size
        self.entity.game_objects.game.display.render(self.entity.image, self.empty, shader = self.entity.game_objects.shaders['dissolve'])#shader render
        self.entity.image = self.empty.texture

        self.entity.game_objects.shaders['bloom']['targetColor'] = self.colour[0:3]

class Tint(Shader_states):#challaenge momutment use it
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['tint']
        self.colour = kwarg.get('colour', [0,0,0,0])

    def draw(self):
        self.entity.shader['colour'] = self.colour

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')

class Blur(Shader_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['blur']
        self.blur_radius = 0.1

    def update(self):
        self.blur_radius += (1.1 - self.blur_radius) * 0.06
        self.blur_radius = min(1.1, self.blur_radius)

    def draw(self):
        self.entity.shader['blurRadius'] = self.blur_radius

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')

class Palette_swap(Shader_states):#droplet use it
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['palette_swap']

    def draw(self):
        self.entity.shader['number_colour'] = len(self.entity.original_colour)
        for index, color in enumerate(self.entity.original_colour):
            self.entity.shader['original_' + str(index)] = color
            self.entity.shader['replace_' + str(index)] = self.entity.replace_colour[index]

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')

class Outline(Shader_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['outline']
        self.time = 0

    def update(self):
        self.time +=1

    def draw(self):        
        #self.entity.shader['TIME'] = self.time
        return
        self.entity.shader['color_gradiant'] = self.entity.image
        self.entity.shader['AuraProgres'] = self.time*0.01

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')