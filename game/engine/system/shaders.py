from engine import constants as C
import math, numpy as np
import moderngl

class Shaders():
    def __init__(self, post_process):
        self.post_process = post_process#TODO change this to game_objects

    def update_render(self, dt):
        pass

    def set_uniforms(self, **kwargs):#is also called from screen layers
        pass

    def draw(self, temp_layer, input_layer):#called for screen pp (small resolution) and composiite pp (scaled resolution)
        """Draw to intermediate texture for pipeline"""
        pass

    def draw_to_composite(self, temp_layer, final_layer):#only called for composite pp -> sacled resoltuoin
        """Draw final result back to composite_screen"""
        pass

class Vignette(Shaders):
    def __init__(self, post_process, **kwargs):
        super().__init__(post_process)
        self.colour = kwargs.get('colour', [0.0, 0.0, 0.0, 1.0])
        self.vignette_intensity = kwargs.get('vignette_intensity', 1.0)
        self.vignette_opacity = kwargs.get('vignette_opacity', 0.1)  # More visible

    def set_uniforms(self, **kwargs):
        shader = self.post_process.game_objects.shaders['vignette']

        shader['colour'] = self.colour
        shader['vignette_intensity'] = self.vignette_intensity
        shader['vignette_opacity'] = self.vignette_opacity

    def draw(self, temp_layer, composite_screen):
        """For intermediate rendering in pipeline"""
        self.set_uniforms()
        #print(temp_layer.size, composite_screen.size)
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

    def update_render(self, dt):
        self.duration -= dt
        if self.duration < 0:
            self.post_process.remove_shader('chromatic_aberration')

    def draw(self, temp_layer, composite_screen):#needs the screen
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['chromatic_aberration'])#shader render
        return temp_layer

    def draw_to_composite(self, temp_layer, composite_screen):
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer)#copy the screen
        #composite_screen.clear(0,0,0,0)        
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader=self.post_process.game_objects.shaders['chromatic_aberration'])

class Blur(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.radius = kwarg.get('radius',1)

    def set_radius(self, radius):
        self.radius = radius

    def draw(self, temp_layer, composite_screen):#needs the screen
        self.post_process.game_objects.shaders['blur']['blurRadius'] = self.radius
        self.post_process.game_objects.game.display.use_premultiplied_alpha_mode()
        #self.post_process.game_objects.game.display.use_alpha_blending(False)#remove thr black outline
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer, shader = self.post_process.game_objects.shaders['blur'])#shader render
        self.post_process.game_objects.game.display.use_standard_alpha_mode()
        #self.post_process.game_objects.game.display.use_alpha_blending(True)#remove thr black outline
        return temp_layer

    def draw_to_composite(self, temp_layer, composite_screen):
        self.post_process.game_objects.shaders['blur']['blurRadius'] = self.radius
        self.post_process.game_objects.game.display.render(composite_screen.texture, temp_layer)#copy the screen
        self.post_process.game_objects.game.display.render(temp_layer.texture, composite_screen, shader=self.post_process.game_objects.shaders['blur'])    

class Blur_fast(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.radius = kwarg.get('radius',1)
        self.downsample = max(1, int(kwarg.get('downsample', 1)))#e.g. 2 or 4
        self.weights = self.make_weights(self._effective_radius())
        self.layer = self.post_process.game_objects.game.display.make_layer(post_process.game_objects.game.window_size)

        if self.downsample > 1:
            size = post_process.game_objects.game.window_size
            down_w = max(1, int(size[0] / self.downsample))
            down_h = max(1, int(size[1] / self.downsample))
            self._down_size = (down_w, down_h)
            self.down_layer = self.post_process.game_objects.game.display.make_layer(self._down_size)
            self.down_temp = self.post_process.game_objects.game.display.make_layer(self._down_size)

    def _effective_radius(self):
        return self.radius / float(self.downsample)

    def _ensure_downsample_layers(self, size):
        down_w, down_h = self._down_size
        down_scale = (down_w / size[0], down_h / size[1])
        up_scale = (size[0] / down_w, size[1] / down_h)
        return self.down_layer, self.down_temp, down_scale, up_scale

    def _set_filter(self, textures, flt):
        prev = []
        for tex in textures:
            if tex is None:
                prev.append(None)
                continue
            prev.append(tex.filter)
            tex.filter = flt
        return prev

    def _restore_filter(self, textures, prev):
        for tex, old in zip(textures, prev):
            if tex is None or old is None:
                continue
            tex.filter = old

    def make_weights(self, radius_float):
        """
        radius_float: blur 'radius' as float (e.g. 2.5)
        returns: numpy array of length MAX_KERNEL (dtype float32) with normalized weights
        """
        MAX_KERNEL = 64
        # If radius is very small, treat as no blur (single tap)
        if radius_float <= 0.01:
            w = np.zeros(MAX_KERNEL, dtype='f4')
            w[0] = 1.0
            return w

        # Use sigma = radius_float for the gaussian spread (common convention)
        sigma = max(radius_float, 0.001)

        # kernel half-size (integer). ceil so we include enough samples for the float radius.
        r = int(math.ceil(radius_float))

        # Build weights for i in [-r .. r]
        weights = []
        for i in range(-r, r + 1):
            x = float(i)
            weights.append(math.exp(-0.5 * (x * x) / (sigma * sigma)))

        # normalize
        s = sum(weights)
        weights = [w / s for w in weights]

        # pad to MAX_KERNEL
        if len(weights) > MAX_KERNEL:
            raise ValueError(f"kernel size {len(weights)} > MAX_KERNEL {MAX_KERNEL}")
        weights += [0.0] * (MAX_KERNEL - len(weights))

        return np.array(weights, dtype='f4')

    def set_radius(self, radius):        
        self.radius = radius
        self.weights = self.make_weights(self._effective_radius())

    def _apply_blur(self, source_layer, target_layer, intermediate_layer):
        display = self.post_process.game_objects.game.display
        blur = self.post_process.game_objects.shaders['blur_fast']
        effective_radius = self._effective_radius()

        if self.downsample > 1:
            size = source_layer.texture.size
            down_layer, down_temp, down_scale, up_scale = self._ensure_downsample_layers(size)
            prev_filter = self._set_filter(
                [source_layer.texture, down_layer.texture, down_temp.texture],
                (moderngl.LINEAR, moderngl.LINEAR),
            )

            down_layer.clear(0, 0, 0, 0)
            display.render(source_layer.texture, down_layer, scale=down_scale)

            blur['direction'] = (1.0, 0.0)
            blur['weights'] = self.weights
            blur['blurRadius'] = effective_radius
            down_temp.clear(0, 0, 0, 0)
            display.render(down_layer.texture, down_temp, shader=blur)

            blur['direction'] = (0.0, 1.0)
            down_layer.clear(0, 0, 0, 0)
            display.render(down_temp.texture, down_layer, shader=blur)

            display.render(down_layer.texture, target_layer, scale=up_scale)
            self._restore_filter(
                [source_layer.texture, down_layer.texture, down_temp.texture],
                prev_filter,
            )

            return target_layer

        # --- Horizontal ---
        intermediate_layer.clear(0, 0, 0, 0)
        blur['direction'] = (1.0, 0.0)
        blur['weights'] = self.weights
        blur['blurRadius'] = effective_radius

        display.render(source_layer.texture, intermediate_layer, shader=blur)

        # --- Vertical ---
        blur['direction'] = (0.0, 1.0)
        display.render(intermediate_layer.texture, target_layer, shader=blur)

        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply_blur(input_layer, temp_layer, self.layer)

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply_blur(final_layer, final_layer, temp_layer)

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

    def update_render(self, dt):
        self.init_temperature += dt * 0.01
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
        self.target = -1#remove shader when zoom reaches this value. Negatuve so it never reaches this on zoom in.

    def zoom_out(self, **kwarg):
        self.scale = kwarg.get('scale', 1)
        self.rate = kwarg.get('rate', 1)
        self.target = self.scale

    def update_render(self, dt):
        """Smoothly interpolate zoom toward target."""
        self.zoom += (self.scale - self.zoom) * self.rate

        if abs(self.zoom - self.target) < 0.001:# Snap and cleanup if fully zoomed out
            self.zoom = self.target
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

class Speed_lines(Shaders):
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

    def update_render(self, dt):
        self.time += dt * 0.1

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

    def update_render(self, dt):
        self.time += dt * 0.01
        self.duration -= dt
        if self.duration <= 0:
            self.post_process.game_objects.post_process.remove_shader('slowmotion')

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

#For entities
class Aura(Shaders):
    def __init__(self, game_objects):
        self.game_objects = game_objects    
        self.time = 0

    def update_render(self, dt):
        self.time += dt * 0.1
 
    def set_uniforms(self):
        self.game_objects.shaders['aura']['TIME'] = self.time
        self.game_objects.shaders['aura']['AuraProgres'] = 1     

    def draw(self, source_texture, composite_screen):
        """For intermediate rendering in pipeline"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['aura'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip):
        """Final render back to composite_screen"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip = flip, shader=self.game_objects.shaders['aura'])

class Outline(Shaders):
    def __init__(self,game_objects, **kwarg):
        self.game_objects = game_objects    
        self.colour = kwarg.get('colour', [1, 1, 1, 1])
        self.thickness = kwarg.get('thickness', 5)
        self.falloff = kwarg.get('falloff', 0)
        self.time = 0

    def update(self, dt):
        self.time += dt

    def set_uniforms(self):
        self.game_objects.shaders['outline']['outlineColor'] = self.colour
        self.game_objects.shaders['outline']['outlineThickness'] = self.thickness
        self.game_objects.shaders['outline']['outlineAlphaFalloff'] = self.falloff

    def draw(self, source_texture, composite_screen):
        """For intermediate rendering in pipeline"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader = self.game_objects.shaders['outline'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip):
        """Final render back to composite_screen"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip = flip, shader = self.game_objects.shaders['outline']) 
