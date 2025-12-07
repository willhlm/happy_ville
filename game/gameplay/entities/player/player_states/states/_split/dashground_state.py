import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class DashGroundState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashGroundPre(entity), 'main': DashGroundMain(entity), 'post': DashGroundPost(entity)}

    def common_values(self):#called when entering this new state, and will not change during phase changes
        self.dir = self.entity.dir.copy()#copy the direction of the entity, and save it in the state across phases

    def allowed(self):
        return self.entity.flags['grounddash']


class DashGroundPre(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_pre')#the name of the class

        self.dash_length = C.dash_length
        if int(self.entity.velocity[0]) == 0:
            self.dash_length += 1
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))#dust
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_manager.add_modifier('dash', entity = self.entity)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0], vol = 1)
        self.wall_buffer = 3

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        self.entity.acceleration[0] = 0

    def update(self, dt):
        self.jump_dash_timer -= dt
        #self.entity.velocity[1] = 0
        #self.entity.velocity[0] = self.entity.dir[0] * max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.dash_length -= dt
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            self.wall_buffer -= 1
            if self.wall_buffer > 0: return
            if self.entity.acceleration[0] != 0:
                state = input.lower() + '_glide'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('idle')
        elif input == 'interrupt':
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.jump_dash_timer > 0: self.enter_state('dash_jump', to_dash_jump=True)

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.movement_manager.remove_modifier('dash')
        super().enter_state(state, **kwarg)


class DashGroundMain(DashGroundPre):#level one dash: normal
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_main')
        self.dash_length = C.dash_length
        self.jump_dash_timer = C.jump_dash_timer
        self.wall_buffer = 3

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def increase_phase(self):
        self.entity.flags['grounddash'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.ground_dash_timer, self.entity.on_grounddash_timout, 'dash timeout')
        self.entity.shader_state.handle_input('idle')
        if self.entity.game_objects.controller.is_held('lb'):
            self.enter_state('sprint')
        else:
            self.enter_phase('post')#enter run


class DashGroundPost(DashGroundPre):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_post')
        self.entity.movement_manager.remove_modifier('dash')
        self.wall_buffer = 3

    def update(self, dt):
        pass

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press
        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.acceleration[0] = C.acceleration[0] * abs(value[0])#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')#enter run

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            self.enter_state('jump')
            input.processed()

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.currentstate.enter_state(state, **kwarg)


