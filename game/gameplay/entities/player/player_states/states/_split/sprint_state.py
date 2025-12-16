import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class SprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SprintMain(entity), 'post': SprintPost(entity)}#'pre': SprintPre(entity),


class SprintMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprint_multiplier = C.sprint_multiplier
        self.sprint_time_threshold = 10

    def enter(self, **kwarg):
        self.sprint_time = 0
        self.entity.animation.play('sprint_main', f_rate=0.22)

    def update(self, dt):
        self.sprint_time += dt
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall', allow_sprint=True)#fall pre
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            if self.sprint_time > self.sprint_time_threshold:
                input.processed()
                self.enter_state('jump_sprint')#main

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()
        elif event[-1]=='lb':
            self.enter_phase('post')

    def handle_movement(self,event):
        value = event['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * self.sprint_multiplier#always positive, add acceleration to entity

        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')


class SprintPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sprint_post')

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall', allow_sprint=True)#pre
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')#main

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')#enter run


