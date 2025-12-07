import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class WallGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallGlide(entity, animation_name = 'wall_glide_main')}#{'pre': WallGlide(entity, animation_name = 'wall_glide_pre'), 'main': WallGlide(entity, animation_name = 'wall_glide_main')}


class WallGlide(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)#the name of the class
        self.entity.flags['ground'] = False#used for jumping: sets to false in cayote timer and in jump state
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.movement_manager.add_modifier('wall_glide')
        if self.entity.collision_types['right']:
            self.dir = [1,0]
        else:#left
            self.dir = [-1,0]
        self.timer_init = 6
        self.timer = self.timer_init
        self.count_timer = False

    def update(self, dt):
        if self.count_timer:
            self.timer -= dt
            if self.timer <= 0:
                self.fall()
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.velocity[0] = 0
            self.enter_state('fall', wall_dir = self.dir)
        else:
            self.entity.velocity[0] += self.entity.dir[0] * 0.2

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('wall_jump', wall_dir = self.dir)
        elif event[-1] == 'lb':
            input.processed()
            self.enter_state('dash_ground')
            self.entity.dir[0] *= -1

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        curr_dir = self.entity.dir[0]

        if value[0] * curr_dir < 0:
            self.count_timer = True
        elif value[0] * curr_dir > 0:
            self.count_timer = False
            self.timer = self.timer_init

    def fall(self):
        self.entity.velocity[0] = -self.entity.dir[0]*2
        self.enter_state('fall', wall_dir = self.dir)

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def exit(self):
        # cleanup on leaving wall_glide
        self.entity.movement_manager.remove_modifier('wall_glide')



