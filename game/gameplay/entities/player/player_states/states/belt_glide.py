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
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')
        self.entity.movement_manager.add_modifier('wall_glide', authoritative = True)
        if self.entity.collision_types['right']:
            self.dir = [1, 0]
        else:
            self.dir = [-1, 0]

    def update(self, dt):
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.velocity[0] = -self.dir[0] * 10
                self.entity.velocity[1] = -7
                self.enter_state('jump')
            else:
                self.entity.velocity[0] = -self.entity.dir[0] * 10
                self.enter_state('fall')
        elif input.name == 'lb' and self.entity.currentstate.states.get('wall_glide'):
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
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')
        elif value[0] == 0:
            self.entity.velocity[0] = -self.entity.dir[0] * 2
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def enter_state(self, input):
        self.entity.movement_manager.remove_modifier('wall_glide')
        super().enter_state(input)
