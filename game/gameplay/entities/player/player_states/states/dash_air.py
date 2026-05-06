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
        self.entity.shader_state.add_shader('mb')
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))
        self.entity.end_coyote_time()
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
        if input == 'interrupt':
            self.entity.shader_state.remove_shader('mb')
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self, input):
        pass

    def handle_release_input(self, input):
        if input.name == 'lb':
            self.entity.flags['sprint_chain_active'] = False
        input.processed()

    def exit(self):
        self.entity.shader_state.remove_shader('mb')
        self.entity.movement_manager.remove_modifier('dash')

    def land_from_dash(self):
        should_sprint = self.entity.game_objects.controller.is_held('lb') and self.entity.flags['sprint_chain_active']
        self.entity.flags['sprint_chain_active'] = False
        if should_sprint:
            self.enter_state('sprint')
        else:
            self.enter_state('land', phase = 'soft')

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            self.land_from_dash()
            return

        if self.entity.has_collision_kind('belt') or self.entity.has_collision_kind('Wall'):
            self.entity.shader_state.remove_shader('mb')
            if self.entity.acceleration[0] != 0:
                if self.entity.has_collision_kind('belt'):
                    self.enter_state('belt_glide')
                else:
                    self.enter_state('wall_glide')
            else:
                self.enter_state('idle')


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

    def handle_release_input(self, input):
        if input.name == 'lb':
            self.entity.flags['sprint_chain_active'] = False
        input.processed()

    def exit_state(self):
        if self.dash_length < 0:
            self.entity.flags['sprint_chain_active'] = self.entity.game_objects.controller.is_held('lb')
            self.entity.movement_manager.add_modifier('air_boost', friction_x = 0.18, entity = self.entity)
            self.enter_state('fall')

    def increase_phase(self):
        self.entity.shader_state.remove_shader('mb')
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
        self.entity.flags['sprint_chain_active'] = self.entity.game_objects.controller.is_held('lb')
        self.entity.movement_manager.add_modifier('air_boost', entity = self.entity)
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('fall')

    def handle_press_input(self, input):
        pass

    def handle_release_input(self, input):
        if input.name == 'lb':
            self.entity.flags['sprint_chain_active'] = False
        input.processed()

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.remove_shader('mb')
        self.entity.currentstate.enter_state(state, **kwarg)
