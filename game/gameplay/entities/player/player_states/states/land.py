from .base_composite import CompositeState
from .base_state import PhaseBase


class LandState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {"soft": LandSoftMain(entity), "hard": LandHardMain(entity)}


class LandSoftMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("land_soft_main")

    def handle_movement(self, axes):
        value = axes.move
        if 0.1 < abs(value[0]) < 0.65:
            self.enter_state("walk")
        elif abs(value[0]) >= 0.65:
            self.enter_state("run")

    def handle_press_input(self, input):
        if input.name == "jump":
            input.processed()
            self.enter_state("jump")
        elif input.name == "ability":
            input.processed()
            self.do_ability()
        elif input.name == "dash":
            input.processed()
            self.enter_state("dash_ground")
        elif input.name == "attack":
            input.processed()
            self.swing_sword("ground")

    def handle_release_input(self, input):
        if input.name == "jump":
            input.processed()

    def increase_phase(self):
        self.enter_state("idle")

class LandHardMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("land_hard_main")

    def update(self, dt):
        self.entity.velocity[0] = 0

    def increase_phase(self):
        self.enter_state("idle")
