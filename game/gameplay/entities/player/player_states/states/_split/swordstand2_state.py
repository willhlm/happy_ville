import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class SwordStand2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {#'pre': SwordStandPre(entity, animation_name = 'sword_stand2_pre'),
                       'main': SwordStandMain(entity, animation_name = 'sword_stand2_main'),
                       'post': SwordStandPost(entity, animation_name = 'sword_stand2_post')}#


class SwordStandPre(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        #self.entity.sword.currentstate.enter_state('Slash_1')
        #self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        self.enter_phase('main')


class SwordStandMain(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()

        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.sword.use_sword()

        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press
        if value[0] == 0:
            self.entity.acceleration[0] = 0

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        self.enter_phase('post')


class SwordStandPost(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')

    #def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
    #    value = event['l_stick']#the avlue of the press
    #    if value[0] == 0:
    #        self.entity.acceleration[0] = 0


