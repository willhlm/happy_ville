from engine.render.shader_chain import ShaderChain

from . import effects


class EntityEffectPipeline:
    def __init__(self, entity, state_controller):
        self.entity = entity
        self.state_controller = state_controller
        self.resources = entity.game_objects.layer_resource_pool
        self.size = None
        self.base_layer = None
        self.temp_layer_a = None
        self.temp_layer_b = None
        self.shader_chain = ShaderChain(self._create_shader)
        self.resources.register_pipeline(self)

    @property
    def shaders(self):
        return self.shader_chain.shaders

    def append_shader(self, shader_name, **kwargs):
        self.shader_chain.append_shader(shader_name, **kwargs)

    def remove_shader(self, shader_name):
        self.shader_chain.remove_shader(shader_name)

    def clear_shaders(self):
        self.shader_chain.clear_shaders()

    def has_shaders(self):
        return self.shader_chain.has_shaders()

    def update_render(self, dt):
        self.shader_chain.update_render(dt)

    def clear_textures(self):
        self.base_layer = None
        self.temp_layer_a = None
        self.temp_layer_b = None
        self.size = None

    def invalidate_resources(self):
        self.clear_textures()

    def _define_size(self, size):
        self.size = tuple(size)
        self.base_layer, self.temp_layer_a, self.temp_layer_b = self.resources.acquire_layers(self.size)

    def _ensure_size(self, size):
        if self.size is None or self.size != tuple(size):
            self.clear_textures()
            self._define_size(size)

    def draw(self, base_texture, target, position, flip, angle):
        self._ensure_size(base_texture.size)
        self.base_layer.clear(0, 0, 0, 0)
        self.temp_layer_a.clear(0, 0, 0, 0)
        self.temp_layer_b.clear(0, 0, 0, 0)

        dst = self.temp_layer_a
        src = self.state_controller.draw(
            base_texture,
            self.base_layer,
            position=(0, 0),
            flip=False,
            angle=0,
        )

        shader_items = list(self.shaders.items())
        for index, (_, shader_obj) in enumerate(shader_items):
            is_last_shader = index == len(shader_items) - 1

            if is_last_shader:
                shader_obj.draw_to_composite(src, target, position, flip, angle)
            else:
                src = shader_obj.draw(src, dst)
                dst = self.temp_layer_b if dst is self.temp_layer_a else self.temp_layer_a
                dst.clear(0, 0, 0, 0)

    def _create_shader(self, shader_name, **kwargs):
        shader_class = getattr(effects, shader_name.capitalize())
        return shader_class(self.entity.game_objects, **kwargs)
