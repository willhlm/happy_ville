from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C
from gameplay.entities.visuals.effects.fade_effect import FadeEffect

class DashJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashJumpPre(entity)}

    def allowed(self):
        return self.entity.flags['grounddash']

class DashJumpPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_pre')
        self.dash_length = C.dash_jump_length
        self.entity.velocity = [0, 0]
        if int(self.entity.velocity[0]) == 0:
            self.dash_length += 1
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.movement_manager.add_modifier('dash_jump', entity = self.entity, authoritative = True)
        self.entity.shader_state.add_shader('mb')
        self.entity.flags['ground'] = False
        self.buffer_time = C.jump_dash_wall_timer

    def exit_state(self):
        if self.dash_length < 0:
            self.entity.movement_manager.add_modifier('air_boost', entity = self.entity)
            self.enter_state('fall')

    def handle_movement(self, event):
        self.entity.acceleration[0] = 0

    def enter_state(self, state, **kwarg):
        self.entity.acceleration[1] = C.acceleration[1]
        self.entity.movement_manager.remove_modifier('dash_jump')
        super().enter_state(state, **kwarg)
        self.entity.shader_state.remove_shader('mb')

    def update(self, dt):
        self.entity.game_objects.particles.emit("spirit_aura", pos = self.entity.hitbox.center, n = 1, colour = C.spirit_colour)
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.buffer_time -= dt
        self.dash_length -= dt
        self.exit_state()

    def handle_release_input(self, input):
        if input.name == 'lb':
            self.entity.flags['sprint_chain_active'] = False
        input.processed()

    def land_from_dash_jump(self):
        should_sprint = self.entity.game_objects.controller.is_held('lb') and self.entity.flags['sprint_chain_active']
        self.entity.flags['sprint_chain_active'] = False
        if should_sprint:
            self.enter_state('sprint')
        elif self.entity.acceleration[0] != 0:
            self.enter_state('run')
        else:
            self.enter_state('land', phase = 'soft')

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            self.land_from_dash_jump()
            return

        if self.entity.has_wall_glide_collision():
            hit_facing_wall = (
                self.entity.is_on_wall_side('right') and self.entity.dir[0] > 0
            ) or (
                self.entity.is_on_wall_side('left') and self.entity.dir[0] < 0
            )
            if hit_facing_wall and self.entity.acceleration[0] != 0 and self.buffer_time < 0:
                self.enter_state('wall_glide')

class DashJumpMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_main')

    def handle_movement(self, event):
        pass

class DashJumpPost(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def update(self, dt):
        pass

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_post')

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')
