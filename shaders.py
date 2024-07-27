import constants as C

class Shaders():
    def __init__(self, renderer):
        self.renderer = renderer
        
    def update(self):
        pass

    def set_uniforms(self):
        pass 

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):       
        pass
    
    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):#the final drawing onto the screen
        pass

class Vignette(Shaders):
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)
        self.colour = kwarg.get('colour',[0,0,0,1])#colour

    def set_colour(self, colour):
        self.colour = colour

    def set_uniforms(self):
        self.renderer.game_objects.shaders['vignette']['colour'] = self.colour

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):       
        self.set_uniforms()
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, shader = self.renderer.game_objects.shaders['vignette'])#shader render
        return self.renderer.game_objects.game.screen.texture

class Chromatic_aberration(Shaders):
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)
        self.duration = kwarg.get('duration',20)

    def update(self):
        self.duration -= self.renderer.game_objects.game.dt
        if self.duration < 0:
            self.renderer.game_objects.shader_render.remove_shader('chromatic_aberration')

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):       
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.layer, shader = self.renderer.game_objects.shaders['chromatic_aberration'])#shader render        
        return  self.renderer.layer.texture

    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):#the final drawing onto the screen
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip)        

class Bloom(Shaders):
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)
        self.radius = kwarg.get('bloomRadius',2)#colour
        self.bloomThreshold = kwarg.get('bloomThreshold',0.7)
        self.bloomIntensity = kwarg.get('bloomIntensity',1)#in pixels
        self.bloomTint = kwarg.get('bloomTint',[1,1,1])#between 0 and 1
        self.targetColor = kwarg.get('targetColor',[1,1,1])#between 0 and 1
        self.colorRange = kwarg.get('colorRange',1)#between 0 and 1

    def set_uniforms(self):
        self.renderer.game_objects.shaders['bloom']['bloomRadius'] = self.radius
        self.renderer.game_objects.shaders['bloom']['bloomIntensity'] = self.bloomIntensity
        self.renderer.game_objects.shaders['bloom']['bloomThreshold'] = self.bloomThreshold
        self.renderer.game_objects.shaders['bloom']['bloomTint'] = self.bloomTint
        self.renderer.game_objects.shaders['bloom']['targetColor'] = self.targetColor
        self.renderer.game_objects.shaders['bloom']['colorRange'] = self.colorRange

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):       
        self.set_uniforms()
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.layer, shader = self.renderer.game_objects.shaders['bloom'])#shader render
        return self.renderer.layer.texture
 
    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):#the final drawing onto the screen
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip)        

class White_balance(Shaders):
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)        

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):       
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.layer, shader = self.renderer.game_objects.shaders['white_balance'])#shader render
        return self.renderer.layer.texture

    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):#the final drawing onto the screen
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip)        

class Speed_lines(Shaders):
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)    
        self.time = 0    

    def update(self):
        self.time += self.renderer.game_objects.game.dt*0.1

    def set_uniforms(self):
        self.renderer.game_objects.shaders['noise_perlin']['u_resolution'] = self.renderer.game_objects.game.window_size
        self.renderer.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.renderer.game_objects.shaders['noise_perlin']['scroll'] = [0,0]# [self.parallax[0]*self.game_objects.camera.scroll[0],self.parallax[1]*self.game_objects.camera.scroll[1]]
        self.renderer.game_objects.shaders['noise_perlin']['scale'] = [70,200]

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):  
        self.set_uniforms()     
        self.renderer.game_objects.game.display.render(self.renderer.layer.texture, self.renderer.layer, shader = self.renderer.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.renderer.game_objects.shaders['speed_lines']['TIME'] = self.time 
        self.renderer.game_objects.shaders['speed_lines']['noise'] = self.renderer.layer.texture

        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, shader = self.renderer.game_objects.shaders['speed_lines'])#shader render
            
        return self.renderer.game_objects.game.screen

class Zoom(Shaders):
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)  
        self.scale = kwarg.get('scale', 1)  
        self.center = kwarg.get('center', (0.5, 0.5))  
        self.rate = kwarg.get('rate', 1)  

    def set_uniforms(self):
        self.renderer.game_objects.shaders['zoom']['zoom_amount'] = self.scale
        self.renderer.game_objects.shaders['zoom']['zoom_center'] = self.center

    def update(self):
        self.scale *= self.rate

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):  
        self.set_uniforms()
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.layer, shader = self.renderer.game_objects.shaders['zoom'])#makes a zoomed copy of the screen
        self.renderer.game_objects.game.display.render(self.renderer.layer.texture, self.renderer.game_objects.game.screen, flip = [False, True])#shader render
        return self.renderer.game_objects.game.screen            

#not used below
class Idle(Shaders):#enteties use it
    def __init__(self, renderer, **kwarg):
        super().__init__(renderer)

    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):#the final drawing onto the screen
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip)        

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):
        return base_texture

class Hurt(Shaders):#turn white -> enteties use it
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.next_animation = kwarg.get('next_animation', 'Idle')
        self.colour = kwarg.get('colour', [1,1,1,1])

    def set_uniforms(self):
        self.renderer.game_objects.shaders['colour'] = self.colour

    def update(self):
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion
        if self.duration < 0:
            self.entity.shader_render.append_shader(self.next_animation)   

    def draw(self, base_texture, pos = [0,0], flip = [False, False]):   
        self.set_uniforms()    
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip, shader = self.renderer.game_objects.shaders['colour'])#shader render
        return self.renderer.game_objects.game.screen.texture


class Invincibile(Shaders):#blink white -> enteyties use it
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

    def set_uniforms(self):
        self.entity.shader['time']  = self.time#(colour,colour,colour)            