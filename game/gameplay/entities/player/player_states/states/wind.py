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
        ability = self.entity.abilities.spirit_abilities['Wind']
        spirit_cost = getattr(ability, 'spirit_cost', 0)
        if spirit_cost:
            self.entity.consume_spirit_cost(spirit_cost)
        ability.initiate()

    def increase_phase(self):
        self.enter_state('idle')
