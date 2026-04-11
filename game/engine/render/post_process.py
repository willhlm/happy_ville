from . import shaders
from .shader_chain import ShaderChain

class CompositePipeline:
    def __init__(self, game_objects, default_shader = None, **kwargs):
        self.game_objects = game_objects
        self.shader_chain = ShaderChain(self._create_shader)
        self.temp_layer = game_objects.game.display.make_layer(game_objects.game.display_size)
        if default_shader:
            self.set_shader(default_shader, **kwargs)

    @property
    def shaders(self):
        return self.shader_chain.shaders

    def update_render(self, dt):
        self.shader_chain.update_render(dt)

    def set_shader(self, shader_name, **kwargs):
        self.shader_chain.set_shader(shader_name, **kwargs)

    def append_shader(self, shader_name, **kwargs):
        self.shader_chain.append_shader(shader_name, **kwargs)

    def remove_shader(self, shader_name):
        self.shader_chain.remove_shader(shader_name)

    def clear_shaders(self):
        self.shader_chain.clear_shaders()

    def has_shaders(self):
        return self.shader_chain.has_shaders()

    @property
    def render_size(self):
        return self.game_objects.game.display_size

    def make_layer(self, size=None):
        return self.game_objects.game.display.make_layer(size or self.render_size)

    def apply(self, composite_screen):
        shader_items = list(self.shaders.items())
        if not shader_items:
            return

        for index, (_, shader_obj) in enumerate(shader_items):
            is_last_shader = index == len(shader_items) - 1
            self.temp_layer.clear(0, 0, 0, 0)

            if is_last_shader:
                shader_obj.draw_to_composite(self.temp_layer, composite_screen)
            else:
                composite_screen = shader_obj.draw(self.temp_layer, composite_screen)

    def _create_shader(self, shader_name, **kwargs):
        shader_class = getattr(shaders, shader_name.capitalize())
        return shader_class(self, **kwargs)

class LayerPipeline:
    def __init__(self, game_objects, screen):
        self.game_objects = game_objects
        self.screen = screen
        self.shader_chain = ShaderChain(self._create_shader)
        self.temp_layer_a = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.temp_layer_b = game_objects.game.display.make_layer(game_objects.game.window_size)

    @property
    def shaders(self):
        return self.shader_chain.shaders

    def update_render(self, dt):
        self.shader_chain.update_render(dt)

    def set_shader(self, shader_name, **kwargs):
        self.shader_chain.set_shader(shader_name, **kwargs)

    def append_shader(self, shader_name, **kwargs):
        self.shader_chain.append_shader(shader_name, **kwargs)

    def remove_shader(self, shader_name):
        self.shader_chain.remove_shader(shader_name)

    def clear_shaders(self):
        self.shader_chain.clear_shaders()

    def has_shaders(self):
        return self.shader_chain.has_shaders()

    @property
    def render_size(self):
        return self.game_objects.game.window_size

    def make_layer(self, size=None):
        return self.game_objects.game.display.make_layer(size or self.render_size)

    def apply(self, source_layer, final_target):
        shader_items = list(self.shaders.items())
        if not shader_items:
            self.screen.apply_pp(source_layer, final_target)
            return

        src = source_layer
        dst = self.temp_layer_a

        self.temp_layer_a.clear(0, 0, 0, 0)
        self.temp_layer_b.clear(0, 0, 0, 0)

        for _, shader_obj in shader_items:
            src = shader_obj.draw(dst, src)
            dst = self.temp_layer_b if dst is self.temp_layer_a else self.temp_layer_a
            dst.clear(0, 0, 0, 0)

        self.screen.apply_pp(src, final_target)

    def _create_shader(self, shader_name, **kwargs):
        shader_class = getattr(shaders, shader_name.capitalize())
        return shader_class(self, **kwargs)
