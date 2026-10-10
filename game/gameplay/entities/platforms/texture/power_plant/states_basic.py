import sys

class Basic_states:
    def __init__(self, entity):
        self.entity = entity
        animation_name = type(self).__name__.lower()
        self.entity.animation.play(animation_name)
        self.entity.image = self.entity.sprites[animation_name][0]

    def update(self, dt):
        pass       

    def enter_state(self, newstate, **kwarg):
        state_type = getattr(sys.modules[__name__], newstate.capitalize())
        self.entity.currentstate = state_type(self.entity, **kwarg)

    def increase_phase(self):
        pass

    def handle_input(self, input, **kwarg):
        pass


class Idle(Basic_states):
    def __init__(self, entity):
        super().__init__(entity)
        self.entity.set_collision_enabled(True)

    def handle_input(self, input, **kwarg):
        if input == "land":
            self.enter_state("land")


class Land(Basic_states):
    def __init__(self, entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state("idle")


class Wither(Basic_states):
    def __init__(self, entity):
        super().__init__(entity)
        self.entity.set_collision_enabled(False)
