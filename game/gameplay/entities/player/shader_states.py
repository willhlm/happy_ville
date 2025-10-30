import sys, math
from engine import constants as C

class BaseState():
    def __init__(self,entity):
        self.entity = entity        

    def handle_input(self, input):
        pass

    def update_render(self, dt):
        pass   

    def draw(self, base_texture, target, position, flip):#called from post_process entity and entity_shader_manager
        """Draw base_texture to target using current shader."""
        self.set_uniforms()
        self.entity.game_objects.game.display.render(base_texture, target, position = position, flip = flip, shader = self.shader)#This part is inpricnple npt needed for idle state. However, to fix it, base_txture neeeds to be a layer -> i.e. make all textures into a layer in initialization.
        return target

    def set_uniforms(self):#called before draw
        pass
    
    def enter_state(self, newstate, **kwarg):
        self.entity.shader_state.enter_state(newstate, **kwarg)        

class Idle(BaseState):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['idle']

    def handle_input(self, input, **kwarg):
        if input == 'Hurt':
            self.enter_state('Hurt', **kwarg)
        elif input == 'outline':
            self.enter_state('Outline',  **kwarg)            
        elif input == 'mix_colour':
            self.enter_state('Mix_colour')
        elif input == 'alpha':
            self.enter_state('Alpha')
        elif input == 'tint':
            self.enter_state('Tint', **kwarg)
        elif input == 'blur':
            self.enter_state('Blur')
        elif input == 'motion_blur':
            self.enter_state('MB')
        if input == 'colour':
            self.enter_state('Colour', **kwarg)            

class Hurt(BaseState):#turn white and shake it a bit -> enteties use it
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.shader = self.entity.game_objects.shaders['shock_damage']
        self.next_animation = 'Idle'
        self.time = 0
        self.amplitude = kwarg.get('amplitude', 1) * 0.08
        self.frequency = kwarg.get('frequency', 50)
        self.colour = kwarg.get('colour', [1, 1, 1, 1])
        self.decay_rate = kwarg.get('decay_rate', 5)
        self.direction = kwarg.get('direction', [1,0])
        self.alpha_decay = kwarg.get('alpha_decay', 0.974)

    def set_uniforms(self):
        self.shader['time'] = self.time*0.01
        self.shader['frequency'] = self.frequency
        self.shader['amplitude'] = self.amplitude
        self.colour[-1] *= self.alpha_decay
        self.shader['colour'] = self.colour
        self.shader['decay_rate'] = self.decay_rate
        self.shader['direction'] = self.direction

    def update_render(self, dt):
        self.duration -= dt
        self.time += dt
        if self.duration < 0:
            self.enter_state(self.next_animation)

    def handle_input(self,input,**kwarg):
        if input == 'Invincibile':
            self.next_animation = 'Invincibile'

class Invincibile(BaseState):#blink white -> enteyties use it
    def __init__(self,entity):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['invincible']
        self.duration = C.invincibility_time_player - (C.hurt_animation_length + 1)#a duration which considers the player invinsibility
        self.time = 0

    def update_render(self, dt):
        self.duration -= dt
        self.time += 0.5 * dt
        if self.duration < 0:
            self.enter_state('Idle')

    def set_uniforms(self):
        self.shader['time']  = self.time#(colour,colour,colour)

class Mix_colour(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['mix_colour']
        self.entity.shader['position'] = 0

    def set_uniforms(self):
        self.entity.shader['colour'] = self.entity.colour#higher alpha for lower parallax
        self.entity.shader['new_colour'] = self.entity.new_colour#higher alpha for lower parallax
        self.entity.shader['position'] = max((self.entity.game_objects.player.hitbox.centerx - self.entity.bounds.left)/self.entity.bounds[2],0)

    def handle_input(self,input):
        if input == 'idle':
            self.enter_state('Idle')

class Colour(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity, **kwarg):#colour is a list of 4 floats):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['colour']
        self.colour = kwarg.get('colour', [1,1,1,1])#colour is a list of 4 floats
        
    def set_uniforms(self, dt):
        self.entity.shader['colour'] = self.colour

    def handle_input(self,input):
        if input == 'idle':
            self.enter_state('Idle')

class Alpha(BaseState):#fade screen uses it
    def __init__(self,entity):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['alpha']
        self.alpha = 255

    def update_render(self, dt):
        self.alpha *= 0.9
        if self.alpha < 5:
            self.entity.kill()

    def set_uniforms(self):
        self.shader['alpha'] = self.alpha

class Teleport(BaseState):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 0
        self.entity.shader = entity.game_objects.shaders['teleport']#apply teleport first and then bloom

    def update_render(self, dt):
        self.time += 0.01
        if self.time >= 1:
            self.entity.kill()

    def set_uniforms(self):
        self.entity.shader['progress'] = self.time

class Glow(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity, colour = [100,200,255,100]):
        super().__init__(entity)
        self.colour = colour
        self.entity.shader = self.entity.game_objects.shaders['bloom']
        self.layer1 = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#!! need to move it somewehre in memory

    def set_uniforms(self):
        self.entity.game_objects.shaders['tint']['colour'] = self.colour
        self.entity.game_objects.game.display.render(self.entity.image, self.layer1, shader = self.entity.game_objects.shaders['tint'])#shader render
        self.entity.image = self.layer1.texture

class Shining(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity, colour = [0.39, 0.78, 1,1]):
        super().__init__(entity)
        self.colour = colour
        self.entity.shader = self.entity.game_objects.shaders['shining']
        self.layer1 = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#make a layer ("surface")
        self.time = 0
        self.speed = 0.6

    def update_render(self, dt):
        self.time += dt * 0.01

    def set_uniforms(self):
        self.entity.shader['TIME'] = self.time
        self.entity.shader['tint'] = self.colour
        self.entity.shader['speed'] = self.speed

class Dissolve(BaseState):#disolve and bloom
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.noise_layer = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks
        self.empty = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks
        self.entity.shader = self.entity.game_objects.shaders['bloom']

        self.time = 0
        self.colour = kwarg.get('colour', [1,0,0,1])
        self.size = kwarg.get('size', 0.1)

    def update_render(self, dt):
        self.time += dt * 0.01

    def set_uniforms(self):
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

class Tint(BaseState):#TODO #move to shadders for the entities
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['tint']
        self.colour = kwarg.get('colour', [0,0,0,0])

    def set_uniforms(self):
        self.entity.shader['colour'] = self.colour

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')

class Blur(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['blur']
        self.blur_radius = 0.1

    def update_render(self, dt):
        self.blur_radius += (1.1 - self.blur_radius) * 0.06
        self.blur_radius = min(1.1, self.blur_radius)

    def set_uniforms(self):
        self.shader['blurRadius'] = self.blur_radius

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')

class Palette_swap(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.shader = self.entity.game_objects.shaders['palette_swap']

    def set_uniforms(self):
        self.entity.shader['number_colour'] = len(self.entity.original_colour)
        for index, color in enumerate(self.entity.original_colour):
            self.entity.shader['original_' + str(index)] = color
            self.entity.shader['replace_' + str(index)] = self.entity.replace_colour[index]

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')

class Mb(BaseState):#TODO #move to shadders for the entities
    def __init__(self,entity):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['motion_blur']
        self.dir = [0.04, 0]

    def set_uniforms(self):
        self.shader['dir'] = self.dir
        self.shader['quality'] = 6

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.enter_state('Idle')
        elif input == 'Hurt':
            self.enter_state('Hurt')

class Noise_border(BaseState):#TODO #move to shadders for the entities
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.noise_layer = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks
        self.empty = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks
        self.color_Lookup = self.entity.game_objects.game.display.make_layer(self.entity.image.size)#move wlesewhere, memory leaks

        self.entity.shader = self.entity.game_objects.shaders['noise_border']
        self.time = 0

    def update_render(self, dt):
        self.time += dt * 0.01

    def set_uniforms(self):
        self.empty.clear(0,0,0,0)
        self.entity.game_objects.shaders['noise_perlin']['u_resolution'] = self.entity.image.size
        self.entity.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.entity.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.entity.game_objects.shaders['noise_perlin']['scale'] = [100,100]#"standard"
        self.entity.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader = self.entity.game_objects.shaders['noise_perlin'])#make perlin noise texture


        self.entity.game_objects.shaders['gradient']['numStops'] = 3
        self.entity.game_objects.shaders['gradient']['colors'] = [[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
        self.entity.game_objects.shaders['gradient']['offsets'] = [0.2, 0.5, 0.52]

        self.entity.game_objects.game.display.render(self.empty.texture, self.color_Lookup, shader = self.entity.game_objects.shaders['gradient'])#shader render

        #self.entity.game_objects.shaders['aura']['AuraProgres'] = 1
        self.entity.game_objects.shaders['noise_border']['TIME'] = self.time
        #self.entity.game_objects.shaders['aura']['color_gradiant'] = self.color_Lookup.texture
        self.entity.game_objects.shaders['noise_border']['textureNoise'] = self.noise_layer.texture


        #blit_pos = (round(self.entity.true_pos[0]-self.entity.game_objects.camera_manager.camera.true_scroll[0]), round(self.entity.true_pos[1]-self.entity.game_objects.camera_manager.camera.true_scroll[1]))
        #self.entity.game_objects.game.display.render(self.empty.texture, self.entity.game_objects.game.screen, position = blit_pos, flip = self.entity.dir[0] > 0, shader = self.entity.game_objects.shaders['slash'])#shader render  

class Swirl(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.shader = self.entity.game_objects.shaders['swirl']
        self.ratio = 1

    def update_render(self, dt):
        self.ratio -= dt * 0.01
        self.ratio = max(0, self.ratio)
        if self.ratio <= 0:
            self.enter_state('Idle')

    def set_uniforms(self):        
        self.shader['ratio'] = self.ratio        

