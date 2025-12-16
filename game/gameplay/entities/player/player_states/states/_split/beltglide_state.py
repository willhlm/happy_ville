import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class BeltGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BeltGlide(entity, animation_name = 'wall_glide_pre'), 'main': BeltGlide(entity, animation_name = 'wall_glide_main')}


class BeltGlide(PhaseBase):#same as wall glide but only jump if wall_glide has been unlocked
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)#the name of the class
        self.entity.flags['ground'] = True#used for jumping: sets to false in cayote timer and in jump state
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.movement_manager.add_modifier('wall_glide')
        if self.entity.collision_types['right']:
            self.dir = [1,0]
        else:
            self.dir = [-1,0]

    def update(self, dt):#is needed
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.velocity[0] = -self.dir[0]*10
                self.entity.velocity[1] = -7#to get a vertical velocity
                self.enter_state('jump')
            else:
                self.entity.velocity[0] = -self.entity.dir[0]*10
                self.enter_state('fall')
        elif event[-1] == 'lb':
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.dir[0] *= -1
                input.processed()
                self.enter_state('dash_ground')

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        curr_dir = self.entity.dir[0]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

        if value[0] * curr_dir < 0:#change sign
            self.entity.velocity[0] = self.entity.dir[0]*2
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')
        elif value[0] == 0:#release
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def enter_state(self,input):#reset friction before exiting this state
        self.entity.movement_manager.remove_modifier('wall_glide')
        super().enter_state(input)


