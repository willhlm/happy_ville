from .base_composite import CompositeState
from .sword_base import SwordAir

class SwordAir1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air1_main')}

class SwordAir2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air2_main')}

class SwordAirMain(SwordAir):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.sword.use_sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.projectiles.add(self.entity.sword)

    def increase_phase(self):
        self.enter_state('fall')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('run')
            else:
                self.enter_state('idle')