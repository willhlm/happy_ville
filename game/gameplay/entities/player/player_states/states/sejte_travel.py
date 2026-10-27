from .base_composite import CompositeState
from .base_state import PhaseBase


class SejteTravelState(CompositeState):
    """Temporary presentation state shared by Sejte departure and arrival."""

    def __init__(self, entity):
        super().__init__(entity)
        self.interaction_enabled = False
        self.phases = {
            'depart': SejteTravelDepart(entity),
            'arrive': SejteTravelArrive(entity),
        }


class SejteTravelPhase(PhaseBase):
    def enter(self, **kwargs):
        self.entity.reset_movement()
        self.entity.velocity = [0, 0]
        self.entity.animation.play('fall_main')
        self.entity.hit_component.set_invincibility(True)

    def exit(self):
        self.entity.shader_state.enter_state('Idle')
        self.entity.hit_component.set_invincibility(False)

    def handle_movement(self, axes):
        pass

    def handle_input(self, input_name, **kwargs):
        if input_name == 'finish':
            self.enter_state('idle')


class SejteTravelDepart(SejteTravelPhase):
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.entity.shader_state.enter_state(
            'Alpha',
            alpha=255,
            fade_rate=0.88,
            kill_threshold=3,
            on_complete=lambda: None,
        )


class SejteTravelArrive(SejteTravelPhase):
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.entity.shader_state.enter_state(
            'Materialize',
            duration=35,
        )
