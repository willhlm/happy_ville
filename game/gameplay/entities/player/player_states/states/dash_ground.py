from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.entities.visuals.cosmetics import Dusts

class DashGroundState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashGroundPre(entity), 'main': DashGroundMain(entity), 'post': DashGroundPost(entity)}

    def common_values(self):
        self.dir = self.entity.dir.copy()

    def allowed(self):
        return self.entity.flags['grounddash']

class DashGroundPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_pre')
        self.dash_length = C.dash_length
        if int(self.entity.velocity[0]) == 0:
            self.dash_length += 1
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_manager.add_modifier('dash', entity = self.entity, authoritative = True)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0], vol = 1)
        self.wall_buffer = 3
        self.entity.dir[0] = kwarg.get('dir', self.entity.dir[0])

    def handle_movement(self, event):
        self.entity.acceleration[0] = 0

    def update(self, dt):
        self.jump_dash_timer -= dt
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.dash_length -= dt
        self.entity.game_objects.particles.emit("spirit_aura", pos = self.entity.hitbox.center, n = 1, colour = C.spirit_colour)
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            self.wall_buffer -= 1
            if self.wall_buffer > 0:
                return
            if self.entity.acceleration[0] != 0:
                state = input.lower() + '_glide'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('idle')
        elif input == 'interrupt':
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            if self.jump_dash_timer > 0:
                self.enter_state('dash_jump', to_dash_jump = True)

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.movement_manager.remove_modifier('dash')
        super().enter_state(state, **kwarg)


class DashGroundMain(DashGroundPre):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_main')
        self.dash_length = C.dash_length
        self.jump_dash_timer = C.jump_dash_timer
        self.wall_buffer = 3

    def handle_press_input(self, input):
        input.processed()

    def increase_phase(self):
        self.entity.flags['grounddash'] = False
        self.entity.game_objects.timer_manager.start_timer(C.ground_dash_timer, self.entity.on_grounddash_timout, 'dash_timeout')
        self.entity.shader_state.handle_input('idle')
        if self.entity.game_objects.controller.is_held('lb'):
            self.enter_state('sprint')
        else:
            self.enter_phase('post')


class DashGroundPost(DashGroundPre):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_post')
        self.entity.movement_manager.remove_modifier('dash')
        self.wall_buffer = 3

    def update(self, dt):
        pass

    def handle_movement(self, axes):
        value = axes.move
        self.entity.acceleration[0] = C.acceleration[0] * abs(value[0])
        self.entity.dir[1] = -value[1]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')

    def handle_press_input(self, input):
        if input.name == 'a':
            self.enter_state('jump')
            input.processed()

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.currentstate.enter_state(state, **kwarg)