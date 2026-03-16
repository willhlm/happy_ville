from .base_composite import CompositeState
from .base_state import PhaseAirBase
from engine import constants as C

class JumpSprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': JumpSprintPre(entity), 'main': JumpSprintMain(entity), 'post': JumpSprintPost(entity)}

class JumpSprintPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_sprint_pre')
        self.air_timer = 10
        self.entity.flags['ground'] = False

    def update(self, dt):
        self.air_timer -= dt
        if self.air_timer >= 0:
            self.entity.velocity[1] = C.jump_vel_player
            self.entity.velocity[0] = self.entity.dir[0] * 10
        else:
            self.enter_phase('main')

class JumpSprintMain(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_sprint_main')
        self.air_timer = kwarg.get('air_timer', C.air_timer)

    def update(self, dt):
        self.entity.velocity[0] += self.entity.dir[0]

    def handle_input(self, input):
        if input == 'Ground':
            self.enter_phase('post')

class JumpSprintPost(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_sprint_post')

    def handle_movement(self, event):
        self.entity.acceleration[0] = 0

    def update(self, dt):
        self.entity.velocity[0] += 0.5 * self.entity.dir[0]

    def increase_phase(self):
        self.enter_state('idle')