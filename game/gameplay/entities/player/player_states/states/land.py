from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C

class LandState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'soft': LandSoftMain(entity), 'hard': LandHardMain(entity)}

class LandSoftMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('land_soft_main')

    def handle_movement(self, axes):
        value = axes.move
        if 0.1 < abs(value[0]) < 0.65:
            self.enter_state('walk')
        elif abs(value[0]) >= 0.65:
            self.enter_state('run')

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('jump')
        elif input.name == 'b':
            input.processed()
            self.do_ability()
        elif input.name == 'lb':
            input.processed()
            self.enter_state('dash_ground')
        elif input.name == 'x':
            input.processed()
            self.swing_sword()

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def increase_phase(self):
        self.enter_state('idle')

    def swing_sword(self):
        if not self.entity.flags['attack_able']:
            return
        if self.entity.dir[1] > C.down_angle:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < C.down_angle * -1:
            self.enter_state('sword_down')
        else:
            state = 'sword_stand' + str(int(self.entity.sword.swing) + 1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

class LandHardMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('land_hard_main')

    def update(self, dt):
        self.entity.velocity[0] = 0

    def increase_phase(self):
        self.enter_state('idle')