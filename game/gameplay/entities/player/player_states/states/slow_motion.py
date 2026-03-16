from .base_composite import CompositeState
from .base_state import PhaseBase

class SlowMotionState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SlowMotionPre(entity), 'main': SlowMotionMain(entity)}

class SlowMotionPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.acceleration[0] = 0
        self.entity.animation.play('slow_motion_pre')

    def increase_phase(self):
        self.enter_phase('main')

class SlowMotionMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.animation.play('slow_motion_main')
        self.entity.abilities.spirit_abilities['Slow_motion'].initiate()

    def increase_phase(self):
        self.enter_state('idle')