from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C

class SprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SprintMain(entity), 'post': SprintPost(entity)}

class SprintMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprint_multiplier = C.sprint_multiplier
        self.sprint_time_threshold = 10

    def enter(self, **kwarg):
        self.sprint_time = 0
        self.entity.animation.play('sprint_main', f_rate = 0.22)

    def update(self, dt):
        self.sprint_time += dt
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall', allow_sprint = True)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        if input.name == 'a' and self.sprint_time > self.sprint_time_threshold:
            input.processed()
            self.entity.flags['grounddash'] = True
            self.enter_state('dash_jump')

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()
        elif input.name == 'lb':
            self.enter_phase('post')

    def handle_movement(self, axes):
        self.entity.acceleration[0] = C.acceleration[0] * self.sprint_multiplier

        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')

class SprintPost(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sprint_post')

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall', allow_sprint = True)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('jump')

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')