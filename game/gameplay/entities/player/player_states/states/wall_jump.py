from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C
from .jump import JumpMain


class WallJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallJumpMain(entity)}

class WallJumpPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('wall_jump_pre')

    def update(self, dt):
        self.entity.velocity[0] = 0
        self.entity.velocity[1] = 0

    def increase_phase(self):
        self.enter_phase('main')


class WallJumpMain(JumpMain):
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)

    def enter(self, **kwarg):
        super().enter(**kwarg)
        self.entity.animation.play('wall_jump_main')
        self.entity.velocity[0] = -self.entity.dir[0] * 6
        self.ignore_input_timer = 8
        self.accelerate_timer = 15
        self.start_dir = -kwarg.get('wall_dir', [1, 0])[0]
        self.entity.dir[0] = self.start_dir

    def update(self, dt):
        super().update(dt)
        self.ignore_input_timer -= 1
        self.accelerate_timer -= 1

    def handle_movement(self, event):
        super().handle_movement(event)
        if self.ignore_input_timer > 0:
            self.entity.dir[0] = self.start_dir
        if self.accelerate_timer > 0:
            self.entity.acceleration[0] = C.acceleration[0]