class Shaders:
    def __init__(self, post_process):
        self.post_process = post_process

    def update_render(self, dt):
        pass

    def set_uniforms(self, **kwargs):
        pass

    def draw(self, temp_layer, input_layer):
        pass

    def draw_to_composite(self, temp_layer, final_layer):
        pass

    @classmethod
    def flush_cache(cls):
        pass
