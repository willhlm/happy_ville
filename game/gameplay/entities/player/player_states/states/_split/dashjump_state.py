import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class DashJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashJumpPre(entity)}#, 'main': DashJumpMain(entity), 'post': DashJumpPost(entity)}

    def allowed(self):
        return self.entity.flags['grounddash']



class DashJumpPre(PhaseBase):#enters from ground dash pre
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_pre')#the name of the class
        self.dash_length = C.dash_jump_length

        #normalize velocity regardless of previous state
        self.entity.velocity = [0, 0]

        if int(self.entity.velocity[0]) == 0:
            self.dash_length += 1
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.movement_manager.add_modifier('dash_jump', entity = self.entity)
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.flags['ground'] = False
        self.buffer_time = C.jump_dash_wall_timer        

    def exit_state(self):
        if self.dash_length < 0:
            self.entity.movement_manager.add_modifier('air_boost', entity = self.entity)
            self.enter_state('fall')

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        self.entity.acceleration[0] = 0

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input =='belt':
            if self.entity.collision_types['right'] and self.entity.dir[0] > 0 or self.entity.collision_types['left'] and self.entity.dir[0] < 0:
                if self.entity.acceleration[0] != 0:
                    if self.buffer_time < 0:
                        state = input.lower() + '_glide'
                        self.enter_state(state, **kwarg)

    def enter_state(self, state):
        self.entity.acceleration[1] = C.acceleration[1]
        self.entity.movement_manager.remove_modifier('dash_jump')
        super().enter_state(state)
        self.entity.shader_state.handle_input('idle')

    def update(self, dt):
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.buffer_time -= dt
        self.dash_length -= dt
        self.exit_state()


