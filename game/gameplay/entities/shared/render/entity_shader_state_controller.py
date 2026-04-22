from . import shader_states


class EntityShaderStateController:
    def __init__(self, entity, default="idle", **kwargs):
        self.entity = entity
        self.current_state = None
        self.enter_state(default, **kwargs)

    def enter_state(self, new_state, **kwargs):
        state_class = getattr(shader_states, new_state.capitalize())
        self.current_state = state_class(self.entity, **kwargs)

    def handle_input(self, input_name, **kwargs):
        self.current_state.handle_input(input_name, **kwargs)

    def update_render(self, dt):
        self.current_state.update_render(dt)

    def draw(self, base_texture, target, position, flip=False, angle=0):
        return self.current_state.draw(base_texture, target, position, flip, angle)
