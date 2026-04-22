class TogglePlatformState:
    animation_name = ""

    def __init__(self, entity):
        self.entity = entity
        self.entity.animation.play(self.animation_name)

    def update(self, dt):
        pass

    def increase_phase(self):
        pass

    def handle_input(self, input_name):
        pass


class ErectState(TogglePlatformState):
    animation_name = "erect"

    def __init__(self, entity):
        super().__init__(entity)
        self.entity.set_collision_enabled(True)

    def handle_input(self, input_name):
        if input_name in {"transform", "Transform", "Off", "off"}:
            self.entity.set_toggle_state("transform_down")


class TransformDownState(TogglePlatformState):
    animation_name = "transform_down"

    def handle_input(self, input_name):
        if input_name in {"transform", "Transform", "On", "on"}:
            self.entity.set_toggle_state("transform_up")

    def increase_phase(self):
        self.entity.set_toggle_state("down")


class TransformUpState(TogglePlatformState):
    animation_name = "transform_up"

    def handle_input(self, input_name):
        if input_name in {"transform", "Transform", "Off", "off"}:
            self.entity.set_toggle_state("transform_down")

    def increase_phase(self):
        self.entity.set_toggle_state("erect")


class DownState(TogglePlatformState):
    animation_name = "down"

    def __init__(self, entity):
        super().__init__(entity)
        self.entity.set_collision_enabled(False)

    def handle_input(self, input_name):
        if input_name in {"transform", "Transform", "On", "on"}:
            self.entity.set_toggle_state("transform_up")


STATE_TYPES = {
    "erect": ErectState,
    "transform_down": TransformDownState,
    "transform_up": TransformUpState,
    "down": DownState,
}
