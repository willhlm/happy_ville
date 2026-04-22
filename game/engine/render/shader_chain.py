class ShaderChain:
    def __init__(self, create_shader):
        self._create_shader = create_shader
        self.shaders = {}

    def update_render(self, dt):
        for shader_obj in list(self.shaders.values()):
            shader_obj.update_render(dt)

    def set_shader(self, shader_name, **kwargs):
        self.clear_shaders()
        self.append_shader(shader_name, **kwargs)

    def append_shader(self, shader_name, **kwargs):
        self.shaders[shader_name] = self._create_shader(shader_name, **kwargs)

    def remove_shader(self, shader_name):
        self.shaders.pop(shader_name, None)

    def clear_shaders(self):
        self.shaders = {}

    def has_shaders(self):
        return bool(self.shaders)
