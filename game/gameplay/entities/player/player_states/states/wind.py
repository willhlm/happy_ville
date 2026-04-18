from .base_composite import CompositeState
from .base_state import PhaseBase

class WindState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WindMain(entity)}

class WindMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self):
        self.entity.animation.play('wind_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Wind'].initiate()

    def increase_phase(self):
        self.enter_state('idle')


