from .base_composite import CompositeState
from .base_state import PhaseBase

class InvisibleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': Invisible(entity)}

class Invisible(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('invisible')


