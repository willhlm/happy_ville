from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.entities.visuals.cosmetics import Dusts
from .dash_ground import DashGroundPre

class DashAirState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashAirPre(entity), 'main': DashAirMain(entity), 'post': DashAirPost(entity)}

class DashAirPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_air_pre')
        if 'air_boost' in self.entity.movement_manager.modifiers.keys():
            self.entity.movement_manager.remove_modifier('air_boost')

        self.dash_length = C.dash_length
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_manager.add_modifier('dash', entity = self.entity, authoritative = True)
        self.entity.velocity[1] *= 0
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0], vol = 1)
        wall_dir = kwarg.get('wall_dir', False)
        if wall_dir:
            self.entity.dir[0] = -wall_dir[0]

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
            self.entity.shader_state.handle_input('idle')
            if self.entity.acceleration[0] != 0:
                state = input.lower() + '_glide'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('idle')
        elif input == 'interrupt':
            self.entity.shader_state.handle_input('idle')
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self, input):
        pass

    def exit(self):
        self.entity.shader_state.handle_input('idle')
        self.entity.movement_manager.remove_modifier('dash')


class DashAirMain(DashGroundPre):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_air_main')
        self.dash_length = C.dash_length
        self.jump_dash_timer = C.jump_dash_timer
        self.wall_buffer = 3

    def handle_press_input(self, input):
        input.processed()

    def exit_state(self):
        if self.dash_length < 0:
            self.entity.movement_manager.add_modifier('air_boost', friction_x = 0.18, entity = self.entity)
            self.enter_state('fall', allow_sprint = True)

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')
        self.enter_phase('post')


class DashAirPost(DashGroundPre):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_air_post')
        self.entity.movement_manager.remove_modifier('dash')
        self.entity.movement_manager.add_modifier('air_boost', friction_x = 0.18, entity = self.entity)
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
        self.entity.movement_manager.add_modifier('air_boost', entity = self.entity)
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('fall', allow_sprint = True)

    def handle_press_input(self, input):
        pass

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.currentstate.enter_state(state, **kwarg)