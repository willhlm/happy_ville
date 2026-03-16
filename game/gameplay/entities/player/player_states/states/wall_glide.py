from .base_composite import CompositeState
from .base_state import PhaseBase

class WallGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallGlide(entity, animation_name = 'wall_glide_main')}

class WallGlide(PhaseBase):
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
        self.timer_init = 6
        self.timer = self.timer_init
        self.count_timer = False

    def update(self, dt):
        if self.count_timer:
            self.timer -= dt
            if self.timer <= 0:
                self.fall()
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:
            self.entity.velocity[0] = 0
            self.enter_state('fall', wall_dir = self.dir)
        else:
            self.entity.velocity[0] += self.entity.dir[0] * 0.2

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('wall_jump', wall_dir = self.dir)
        elif input.name == 'lb':
            input.processed()
            self.enter_state('dash_ground', dir = -self.entity.dir[0])

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def handle_movement(self, axes):
        value = axes.move
        curr_dir = self.entity.dir[0]
        if value[0] * curr_dir < 0:
            self.count_timer = True
        elif value[0] * curr_dir > 0:
            self.count_timer = False
            self.timer = self.timer_init

    def fall(self):
        self.entity.velocity[0] = -self.entity.dir[0] * 2
        self.enter_state('fall', wall_dir = self.dir)

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def exit(self):
        self.entity.movement_manager.remove_modifier('wall_glide')