class WindmillState:
    """Base for persistent windmill presentation and future state behaviour."""

    state_name = ""

    def __init__(self, entity):
        self.entity = entity
        self.entity.animation.play(self.state_name)

    def enter_state(self, state_name):
        self.entity.enter_state(state_name)

    def update(self, dt):
        pass

    def handle_input(self, input_name):
        pass

    def increase_phase(self):
        pass


class Idle(WindmillState):
    state_name = "idle"


class Stuck(WindmillState):
    state_name = "stuck"


class Active(WindmillState):
    state_name = "active"


STATE_TYPES = {
    "idle": Idle,
    "stuck": Stuck,
    "active": Active,
}
