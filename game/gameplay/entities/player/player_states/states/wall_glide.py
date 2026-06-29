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
        self.profile = None
        self.glide_friction = 0

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.movement_controller.interrupt_jump()
        self.entity.end_coyote_time()
        self.entity.flags['grounddash'] = True#allow grounddash after wallglide, but not walljump, to give player more options out of wallglide
        if self.entity.is_on_wall_side('right'):
            self.dir = [1, 0]
        elif self.entity.is_on_wall_side('left'):
            self.dir = [-1, 0]
        else:
            self.dir = [self.entity.dir[0], 0]
        self.entity.dir[0] = self.dir[0]
        self.profile = None
        self.glide_friction = 0
        self.timer_init = 6
        self.timer = self.timer_init
        self.count_timer = False

    def update(self, dt):
        if self.count_timer:
            self.timer -= dt
            if self.timer <= 0:
                self.fall()
        if not self.entity.is_on_wall():
            self.entity.velocity[0] = 0
            self.enter_state('fall', wall_dir = self.dir)
        else:
            self.apply_wall_glide_profile(dt)
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

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            self.enter_state('run')

    def apply_wall_glide_profile(self, dt):
        profile = self.entity.contact_state.get_wall_glide_profile(side=self.get_wall_side())
        if profile != self.profile:
            self.profile = profile
            self.glide_friction = profile['friction_start']
        else:
            self.glide_friction = max(
                profile['friction_end'],
                self.glide_friction - profile['friction_decay'],
            )

        if self.entity.velocity[1] <= 0:
            return

        base_friction = self.entity.friction[1]
        wall_factor = 1 - dt * self.glide_friction
        base_factor = 1 - dt * base_friction
        self.entity.velocity[1] *= wall_factor / base_factor

    def get_wall_side(self):
        return 'right' if self.dir[0] > 0 else 'left'
