import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class SmashSideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SmashSidePre(entity), 'charge': SmashSideCharge(entity), 'main': SmashSideMain(entity), 'post': SmashSidePost(entity)}


class SmashSidePre(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_pre'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.release_input = False#used to check if the input is released, so that the sword can be swung
        self.entity.dir[0] = kwarg['dir']

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] = 0

    def increase_phase(self):
        if self.release_input:
            self.enter_phase('main')
        else:
            self.enter_phase('charge')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='x':
            self.release_input = True


class SmashSideCharge(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_charge'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.time  = 20

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] = 0
        self.time -= dt
        if self.time < 0: self.enter_phase('main')

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def increase_phase(self):
        pass

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='x':
            self.enter_phase('main')


class SmashSideMain(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_main'

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.sword.use_sword()
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.1

    def increase_phase(self):
        self.enter_phase('post')


class SmashSidePost(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_post'

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.1

    def increase_phase(self):
        self.enter_state('idle')


