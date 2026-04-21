from engine import constants as C
from engine.render.blur_kernel import build_gaussian_kernel

class Shaders():
    def __init__(self, post_process):
        self.post_process = post_process

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
        self.vignette_opacity = kwargs.get('vignette_opacity', 0.7)

    def set_uniforms(self, **kwargs):
        shader = self.post_process.game_objects.shaders['vignette']

        shader['colour'] = self.colour
        shader['vignette_intensity'] = self.vignette_intensity
        shader['vignette_opacity'] = self.vignette_opacity

    def _apply(self, source_layer, target_layer):
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['vignette'],
        )
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)

class Chromatic_aberration(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.duration = kwarg.get('duration',20)

    def update_render(self, dt):
        self.duration -= dt
        if self.duration < 0:
            self.post_process.remove_shader('chromatic_aberration')

    def _apply(self, source_layer, target_layer):
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['chromatic_aberration'],
        )
        return target_layer

    def draw(self, temp_layer, input_layer):#needs the screen
        self._apply(input_layer, temp_layer)
        return temp_layer

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)

class Blur(Shaders):#only on composite
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.radius = kwarg.get('radius',1)

    def set_radius(self, radius):
        self.radius = radius

    def _apply(self, source_layer, target_layer):
        self.post_process.game_objects.shaders['blur']['blurRadius'] = self.radius
        self.post_process.game_objects.game.display.use_premultiplied_alpha_mode()
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['blur'],
        )
        self.post_process.game_objects.game.display.use_standard_alpha_mode()
        return target_layer

    def draw(self, temp_layer, input_layer):#needs the screen
        self._apply(input_layer, temp_layer)
        return temp_layer

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)

class Blur_fast(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.radius = float(kwarg.get("radius", 2.0))
        self._r_int = 0
        self._weights = None
        self._rebuild_kernel()

    def _rebuild_kernel(self):# IMPORTANT: 2D blur cost grows as (2r+1)^2. Keep r small (1–4 typical).        
        self._r_int, self._weights = build_gaussian_kernel(self.radius)

    def set_radius(self, radius):
        self.radius = float(radius)
        self._rebuild_kernel()

    def _apply(self, source_layer, target_layer):
        blur = self.post_process.game_objects.shaders["blur_fast"]
        display = self.post_process.game_objects.game.display

        blur["r"] = self._r_int
        blur["weights"] = self._weights
        blur["imageTexture"] = source_layer.texture

        display.render(source_layer.texture, target_layer, shader=blur)
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)

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

    def _apply(self, source_layer, target_layer):
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['bloom'],
        )
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):#the final drawing onto the screen
        self._apply(temp_layer, final_layer)

class Glow(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.glowRadius = kwarg.get('radius',5)
        self.glowThreshold = kwarg.get('threshould',0.4)
        self.glowIntensity = kwarg.get('intensity',10)
        self.targetColor = kwarg.get('target_colour',(1,1,1))
        self.glowColor = kwarg.get('colour',(1,0,0))
        self.colorTolerance = kwarg.get('tolerance',0.2)

    def set_uniforms(self):
        self.post_process.game_objects.shaders['glow']['glowRadius'] = self.glowRadius
        self.post_process.game_objects.shaders['glow']['glowIntensity'] = self.glowIntensity
        self.post_process.game_objects.shaders['glow']['glowThreshold'] = self.glowThreshold
        self.post_process.game_objects.shaders['glow']['targetColor'] = self.targetColor
        self.post_process.game_objects.shaders['glow']['glowColor'] = self.glowColor
        self.post_process.game_objects.shaders['glow']['colorTolerance'] = self.colorTolerance

    def _apply(self, source_layer, target_layer):
        self.set_uniforms()
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['glow'],
        )
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):#the final drawing onto the screen
        self._apply(temp_layer, final_layer)

class White_balance(Shaders):#only on composite
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.temperature = kwarg.get('temperature', 1)
        self.init_temperature = 0

    def update_render(self, dt):
        self.init_temperature += dt * 0.01
        self.init_temperature = min(self.init_temperature, self.temperature)

    def _apply(self, source_layer, target_layer):
        shader = self.post_process.game_objects.shaders['white_balance']
        shader['temperature'] = self.init_temperature
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=shader,
        )
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):#the final drawing onto the screen
        self._apply(temp_layer, final_layer)

class Depth_darken(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.colour = kwarg.get('colour', (0.0, 0.0, 0.0, 0.0))

    def set_uniforms(self):
        self.post_process.game_objects.shaders['depth_darken']['colour'] = self.colour

    def _apply(self, source_layer, target_layer):
        self.set_uniforms()
        display = self.post_process.game_objects.game.display
        #display.use_alpha_blending(False)
        display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['depth_darken'],
        )
        #display.use_alpha_blending(True)
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)

class Zoom(Shaders):#only on composite
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.zoom = 1#zoom scale
        self.center = kwarg.get('center', (0.5, 0.5))
        self.rate = kwarg.get('rate', 1)
        self.scale = kwarg.get('scale', 0.5)
        self.target = -1#remove shader when zoom reaches this value. Negatuve so it never reaches this on zoom in.
        self.work_layer = None
        self.work_size = None

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

    def _ensure_work_layer(self, size):
        if self.work_size != tuple(size):
            if self.work_layer:
                self.work_layer.release()
            self.work_size = tuple(size)
            self.work_layer = self.post_process.make_layer(size)

    def _apply(self, source_layer, target_layer):
        self.set_uniforms()
        self._ensure_work_layer(source_layer.size)
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            self.work_layer,
            shader=self.post_process.game_objects.shaders['zoom'],
        )
        self.post_process.game_objects.game.display.render(
            self.work_layer.texture,
            target_layer,
            flip=[False, True],
        )
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)

class Speed_lines(Shaders):
    def __init__(self, post_process, **kwarg):
        super().__init__(post_process)
        self.colour = kwarg.get('colour', (1,1,1,1))
        window_size = self.post_process.game_objects.game.window_size
        center = kwarg.get('center', (window_size[0] * 0.5, window_size[1] * 0.5))
        self.center = [center[0] / window_size[0], center[1] / window_size[1]]
        self.number = kwarg.get('number', 1)
        self.time = 0
        self.noise_layer = None
        self.empty = None
        self.layer_size = None

    def update_render(self, dt):
        self.time += dt * 0.1

    def _ensure_layers(self, size):
        if self.layer_size != tuple(size):
            if self.noise_layer:
                self.noise_layer.release()
            if self.empty:
                self.empty.release()
            self.layer_size = tuple(size)
            self.noise_layer = self.post_process.make_layer(size)
            self.empty = self.post_process.make_layer(size)

    def set_uniforms(self):
        self.post_process.game_objects.shaders['speed_lines']['TIME'] = self.time
        self.post_process.game_objects.shaders['speed_lines']['noise'] = self.noise_layer.texture
        self.post_process.game_objects.shaders['speed_lines']['line_color'] = self.colour
        self.post_process.game_objects.shaders['speed_lines']['center'] = self.center
        self.post_process.game_objects.shaders['speed_lines']['line_count'] = self.number

    def _apply(self, source_layer, target_layer):
        self._ensure_layers(source_layer.size)
        self.post_process.game_objects.shaders['noise_perlin']['u_resolution'] = source_layer.size
        self.post_process.game_objects.shaders['noise_perlin']['u_time'] = self.time
        self.post_process.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.post_process.game_objects.shaders['noise_perlin']['scale'] = [70,70]
        self.post_process.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.post_process.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.set_uniforms()
        self.post_process.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.post_process.game_objects.shaders['speed_lines'],
        )
        return target_layer

    def draw(self, temp_layer, input_layer):
        return self._apply(input_layer, temp_layer)

    def draw_to_composite(self, temp_layer, final_layer):
        self._apply(temp_layer, final_layer)
