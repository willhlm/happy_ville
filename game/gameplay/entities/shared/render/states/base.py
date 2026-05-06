class BaseState:
    def __init__(self, entity):
        self.entity = entity

    def handle_input(self, input_name, **kwargs):
        pass

    def update_render(self, dt):
        pass

    def draw(self, base_texture, target, position, flip, angle):
        """Draw base_texture to target using current shader."""
        self.set_uniforms()
        self.entity.game_objects.game.display.render(
            base_texture,
            target,
            position=position,
            flip=flip,
            angle=angle,
            shader=self.shader,
        )
        return target

    def set_uniforms(self):
        pass

    def finish(self):
        on_complete = getattr(self, 'on_complete', None)
        if on_complete:
            self.on_complete = None
            on_complete()

    def enter_state(self, newstate, **kwargs):
        self.entity.shader_state.enter_state(newstate, **kwargs)

