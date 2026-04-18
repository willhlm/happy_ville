from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C

class RunState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': RunPre(entity), 'main': RunMain(entity), 'post': RunPost(entity)}

class RunPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('run_pre')
        self.particle_timer = 0
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')

    def update(self, dt):
        self.particle_timer -= dt
        if self.particle_timer < 0:
            self.running_particles()

        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def increase_phase(self):
        self.enter_phase('main')

    def running_particles(self):
        self.particle_timer = 10

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('jump')
        elif input.name == 'lb':
            input.processed()
            self.enter_state('dash_ground')
        elif input.name == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
        elif input.name == 'b':
            input.processed()
            self.do_ability()

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def handle_movement(self, axes):
        super().handle_movement(axes)
        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')

    def swing_sword(self):
        if not self.entity.flags['attack_able']:
            return
        if abs(self.entity.dir[1]) < 0.8:
            state = 'sword_stand' + str(int(self.entity.sword.swing) + 1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0.8:
            self.enter_state('sword_up')

class RunMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('run_main')
        self.particle_timer = 0
        self.sfx_loop_time = 18
        self.sfx_timer = 1

    def update(self, dt):
        self.particle_timer -= dt
        if self.particle_timer < 0:
            pass

        self.sfx_timer -= 1
        if self.sfx_timer == 0:
            self.entity.game_objects.sound.play_sfx(self.entity.sounds['run'][self.sfx_timer % 2], vol = 0.8)
            self.sfx_timer = self.sfx_loop_time

        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def enter_state(self, new_state, **kwarg):
        super().enter_state(new_state, **kwarg)

    def running_particles(self):
        self.particle_timer = 10

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('jump')
        elif input.name == 'lb':
            input.processed()
            self.enter_state('dash_ground')
        elif input.name == 'x':
            input.processed()
            self.swing_sword()
        elif input.name == 'b':
            input.processed()
            self.do_ability()

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def handle_movement(self, axes):
        super().handle_movement(axes)
        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')
        elif abs(self.entity.acceleration[0]) < 0.3:
            self.enter_state('walk', phase = 'main')

    def swing_sword(self):
        if not self.entity.flags['attack_able']:
            return
        if abs(self.entity.dir[1]) < 0.8:
            state = 'sword_stand' + str(int(self.entity.sword.swing) + 1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0.8:
            self.enter_state('sword_up')

class RunPost(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('run_post')

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('jump')
        elif input.name == 'lb':
            input.processed()
            self.enter_state('dash_ground')
        elif input.name == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
        elif input.name == 'b':
            input.processed()
            self.do_ability()

    def handle_movement(self, axes):
        super().handle_movement(axes)
        if self.entity.acceleration[0] != 0:
            self.entity.currentstate.composite_state.enter_phase('pre')

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def swing_sword(self):
        if not self.entity.flags['attack_able']:
            return
        if self.entity.dir[1] == 0:
            state = 'sword_stand' + str(int(self.entity.sword.swing) + 1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0:
            self.enter_state('sword_up')

    def increase_phase(self):
        self.enter_state('idle')