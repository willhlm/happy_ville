import constants as C

class Shaders():
    def __init__(self, post_process):
        self.post_process = post_process

    def update(self):
        pass

    def set_uniforms(self):
        pass

    def draw(self, source_texture, target_texture):
        """Draw to intermediate texture for pipeline"""
        pass

    def draw_to_composite(self, source_texture, composite_screen):
        """Draw final result back to composite_screen"""
        pass

class Vignette(Shaders):
    def __init__(self, post_process, **kwargs):
        super().__init__(post_process)
        self.colour = kwargs.get('colour', [0.0, 0.0, 0.0, 1.0])
        self.vignette_intensity = kwargs.get('vignette_intensity', 1.0)
        self.vignette_opacity = kwargs.get('vignette_opacity', 0.1)  # More visible

    def set_uniforms(self):
        shader = self.post_process.game_objects.shaders['vignette']

        shader['colour'] = self.colour
        shader['vignette_intensity'] = self.vignette_intensity
        shader['vignette_opacity'] = self.vignette_opacity

    def draw(self, temp_layer, composite_screen):
        """For intermediate rendering in pipeline"""
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader=self.post_process.game_objects.shaders['vignette'])
        return composite_screen

    def draw_to_composite(self, temp_layer, composite_screen):
        """Final render back to composite_screen"""
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader=self.post_process.game_objects.shaders['vignette'])

class Chromatic_aberration(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.duration = kwarg.get('duration',20)

    def update(self):
        self.duration -= self.post_process.game_objects.game.dt
        if self.duration < 0:
            self.post_process.remove_shader('chromatic_aberration')

    def draw(self, temp_layer, composite_screen):#needs the screen
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['chromatic_aberration'])#shader render
        return  temp_layer

    def draw_to_composite(self, temp_layer, composite_screen):
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer)#copy the screen
        #composite_screen.clear(0,0,0,0)
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader=self.post_process.game_objects.shaders['chromatic_aberration']      )

class Bloom(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.radius = kwarg.get('bloomRadius',0.5)
        self.bloomThreshold = kwarg.get('bloomThreshold',0.6)
        self.bloomIntensity = kwarg.get('bloomIntensity',10)#in pixels

    def set_uniforms(self):
        self.post_process.game_objects.shaders['bloom']['bloomRadius'] = self.radius
        self.post_process.game_objects.shaders['bloom']['bloomIntensity'] = self.bloomIntensity
        self.post_process.game_objects.shaders['bloom']['bloomThreshold'] = self.bloomThreshold

    def draw(self, temp_layer, composite_screen):
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['bloom'])
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen)
        return composite_screen

    def draw_to_composite(self, temp_layer, composite_screen):#the final drawing onto the screen
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['bloom'])
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen)

class Glow(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.glowRadius = kwarg.get('radius',5)
        self.glowThreshold = kwarg.get('threshould',0.4)
        self.glowIntensity = kwarg.get('intensity',10)
        self.targetColor = kwarg.get('target_colour',(1,0,0))
        self.glowColor = kwarg.get('colour',(1,0,0))
        self.colorTolerance = kwarg.get('tolerance',0)

    def set_uniforms(self):
        self.post_process.game_objects.shaders['glow']['glowRadius'] = self.glowRadius
        self.post_process.game_objects.shaders['glow']['glowIntensity'] = self.glowIntensity
        self.post_process.game_objects.shaders['glow']['glowThreshold'] = self.glowThreshold
        self.post_process.game_objects.shaders['glow']['targetColor'] = self.targetColor
        self.post_process.game_objects.shaders['glow']['glowColor'] = self.glowColor
        self.post_process.game_objects.shaders['glow']['colorTolerance'] = self.colorTolerance

    def draw(self, temp_layer, composite_screen):
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['glow'])
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen)
        return composite_screen

    def draw_to_composite(self, temp_layer, composite_screen):#the final drawing onto the screen
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['glow'])
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen)

class White_balance(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.temperature = kwarg.get('temperature', 0.2)
        self.init_temperature = 0

    def update(self):
        self.init_temperature += self.post_process.game_objects.game.dt * 0.01
        self.init_temperature = min(self.init_temperature, self.temperature)

    def draw(self, temp_layer, composite_screen):
        self.post_process.game_objects.shaders['white_balance']['temperature'] = self.init_temperature
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['white_balance'])
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen)
        return composite_screen

    def draw_to_composite(self, temp_layer, composite_screen):#the final drawing onto the screen
        self.post_process.game_objects.shaders['white_balance']['temperature'] = self.init_temperature
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['white_balance'])
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen)

class Zoom(Shaders):#only zoom in?
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.zoom = 1#zoom scale
        self.center = kwarg.get('center', (0.5, 0.5))
        self.rate = kwarg.get('rate', 1)
        self.scale = kwarg.get('scale', 0.5)
        self.method = 'zoom_in'
        self.methods = {'zoom_out': self.zoom_out, 'zoom_in': self.zoom_in}
        self.zoom_start_timer = C.fps

    def update(self):
        self.methods[self.method]()

    def zoom_in(self):
        self.zoom_start_timer -= self.post_process.game_objects.game.dt
        if self.zoom_start_timer < 0:
            self.zoom -= (self.zoom - self.scale)*self.rate
            self.zoom = max(self.zoom, self.scale)

    def zoom_out(self):
        self.zoom += (1 - self.zoom)*(2*self.rate)
        self.zoom = min(self.zoom, 1)
        if abs(self.zoom - 1) < 0.001:
            self.post_process.remove_shader('zoom')

    def set_uniforms(self):
        self.post_process.game_objects.shaders['zoom']['zoom_amount'] = self.zoom
        self.post_process.game_objects.shaders['zoom']['zoom_center'] = self.center

    def draw(self, temp_layer, composite_screen):
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(composite_screen.texture, self.post_process.temp_layer, shader = self.post_process.game_objects.shaders['zoom'])#makes a zoomed copy of the screen
        self.post_process.game_objects.game.display.render(self.post_process.temp_layer.texture, composite_screen, flip = [False, True])#shader render
        return composite_screen.texture

    def draw_to_composite(self, temp_layer, composite_screen):
        self.draw( temp_layer, composite_screen)

class Speed_lines(Shaders):#TODO, should jusu be a cosmetic, not a screen shader
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.noise_layer = post_process.game_objects.game.display.make_layer(post_process.game_objects.game.window_size)#TODO
        self.empty = post_process.game_objects.game.display.make_layer(post_process.game_objects.game.window_size)#TODO

        self.colour = kwarg.get('colour', (1,1,1,1))
        size = post_process.game_objects.game.window_size
        center = kwarg.get('center', (size[0] * 0.5, size[1] * 0.5))
        self.center = [center[0]/size[0], center[1]/size[1]]
        self.number = kwarg.get('number', 1)
        self.time = 0

    def update(self):
        self.time += self.post_process.game_objects.game.dt * 0.1

    def set_uniforms(self):
        self.post_process.game_objects.shaders['speed_lines']['TIME'] = self.time
        self.post_process.game_objects.shaders['speed_lines']['noise'] = self.noise_layer.texture
        self.post_process.game_objects.shaders['speed_lines']['line_color'] = self.colour
        self.post_process.game_objects.shaders['speed_lines']['center'] = self.center
        self.post_process.game_objects.shaders['speed_lines']['line_count'] = self.number

    def draw(self, temp_layer, composite_screen):
        """For intermediate rendering in pipeline"""
        self.post_process.game_objects.shaders['noise_perlin']['u_resolution'] = self.post_process.game_objects.game.window_size
        self.post_process.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.post_process.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.post_process.game_objects.shaders['noise_perlin']['scale'] = [70,70]
        self.post_process.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.post_process.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.set_uniforms()
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader = self.post_process.game_objects.shaders['speed_lines'])#shader render
        return composite_screen

    def draw_to_composite(self, temp_layer, composite_screen):
        """Final render back to composite_screen"""
        self.draw(temp_layer, composite_screen)

class Slowmotion(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.screen_copy = post_process.game_objects.game.display.make_layer(post_process.game_objects.game.display_size)#TODO
        self.empty = post_process.game_objects.game.display.make_layer(post_process.game_objects.game.display_size)#TODO
        self.empty2 = post_process.game_objects.game.display.make_layer(post_process.game_objects.game.display_size)#TODO

        self.noise_layer = post_process.game_objects.game.display.make_layer(post_process.game_objects.game.display_size)#TODO
        self.time = 0
        self.duration = kwarg.get('duration', 20)

    def update(self):
        self.time += self.post_process.game_objects.game.dt * 0.01
        self.duration -= self.post_process.game_objects.game.dt
        if self.duration <= 0:
            self.post_process.game_objects.shader_render.remove_shader('slowmotion')

    def draw(self, temp_layer, composite_screen):
        self.post_process.game_objects.shaders['noise_perlin']['u_resolution'] = self.post_process.game_objects.game.display_size
        self.post_process.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.post_process.game_objects.shaders['noise_perlin']['scroll'] = [self.post_process.game_objects.camera_manager.camera.scroll[0], -self.post_process.game_objects.camera_manager.camera.scroll[1]]
        self.post_process.game_objects.shaders['noise_perlin']['scale'] = [3, 3]
        self.post_process.game_objects.game.display.render(temp_layer.texture, self.noise_layer, shader=self.post_process.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.post_process.game_objects.game.display.render(composite_screen.texture, self.screen_copy)#big

        self.post_process.game_objects.shaders['slowmotion']['TIME'] = self.time
        self.post_process.game_objects.shaders['slowmotion']['NOISE_TEXTURE'] = self.noise_layer.texture
        self.post_process.game_objects.shaders['slowmotion']['SCREEN_TEXTURE'] = self.screen_copy.texture

        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader = self.post_process.game_objects.shaders['slowmotion'])#shader render
        return composite_screen

    def draw_to_composite(self, temp_layer, composite_screen):
        """Final render back to composite_screen"""
        self.draw(temp_layer, composite_screen)

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
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.layer, flip = flip, shader = self.renderer.game_objects.shaders['colour'])#shader render
        return self.renderer.layer.texture

    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):
        self.set_uniforms()
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip, shader = self.renderer.game_objects.shaders['colour'])#shader render

class Invincibile(Shaders):#blink white -> enteyties use it
    def __init__(self,entity):
        super().__init__(entity)
        self.duration = C.invincibility_time_player - (C.hurt_animation_length + 1)#a duration which considers the player invinsibility
        self.time = 0

    def update(self):
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion
        self.time += 0.5 * self.entity.game_objects.game.dt*self.entity.slow_motion
        if self.duration < 0:
            self.enter_state('Idle')

    def set_uniforms(self):
        self.entity.game_objects.shaders['invincible']['time']  = self.time#(colour,colour,colour)

    def draw_screen(self, base_texture, pos = [0,0], flip = [False, False]):
        self.set_uniforms()
        self.renderer.game_objects.game.display.render(base_texture, self.renderer.game_objects.game.screen, position = pos, flip = flip, shader = self.renderer.game_objects.shaders['invincible'])#shader render
