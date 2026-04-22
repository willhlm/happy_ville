from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C
from engine.utils.functions import sign

class BeltGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BeltGlide(entity, animation_name = 'wall_glide_pre'), 'main': BeltGlide(entity, animation_name = 'wall_glide_main')}

class BeltGlide(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.end_coyote_time()
        self.entity.movement_manager.add_modifier('wall_glide', authoritative = True)
        if self.entity.is_on_wall_side('right'):
            self.dir = [1, 0]
        else:
            self.dir = [-1, 0]

    def update(self, dt):
        if not self.entity.is_on_wall():
            self.enter_state('fall')
            if self.entity.has_collision_kind('Wall'):
                self.entity.begin_coyote_time()

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            if self.entity.has_collision_kind('Wall'):
                self.entity.velocity[0] = -self.dir[0] * 10
                self.entity.velocity[1] = -7
                self.enter_state('jump')
            else:
                self.entity.velocity[0] = -self.entity.dir[0] * 10
                self.enter_state('fall')
        elif input.name == 'lb' and self.entity.has_collision_kind('Wall'):
            input.processed()
            self.enter_state('dash_ground')

    def handle_movement(self, axes):
        value = axes.move
        self.entity.acceleration[0] = C.acceleration[0] * abs(value[0] * 0.8).__ceil__()
        self.entity.dir[1] = -value[1]

        curr_dir = self.entity.dir[0]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

        if value[0] * curr_dir < 0:
            self.entity.velocity[0] = self.entity.dir[0] * 2
            self.enter_state('fall')
            if self.entity.has_collision_kind('Wall'):
                self.entity.begin_coyote_time()
        elif value[0] == 0:
            self.entity.velocity[0] = -self.entity.dir[0] * 2
            self.enter_state('fall')
            if self.entity.has_collision_kind('Wall'):
                self.entity.begin_coyote_time()

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            self.enter_state('run')

    def enter_state(self, input):
        self.entity.movement_manager.remove_modifier('wall_glide')
        super().enter_state(input)
