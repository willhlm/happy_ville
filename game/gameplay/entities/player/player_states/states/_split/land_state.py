import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class LandState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'soft': LandSoftMain(entity), 'hard': LandHardMain(entity)}


class LandSoftMain(PhaseBase):#landing: mainly cosmetic
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['ground'] = True
        self.entity.animation.play('land_soft_main')

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press
        if 0.1 < abs(value[0]) < 0.65:
            self.enter_state('walk')
        elif abs(value[0]) >= 0.65:
            self.enter_state('run')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('idle')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('sword_down')
        else:#right or left
            state = 'sword_stand' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing


class LandHardMain(PhaseBase):#landing: cannot move
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['ground'] = True
        self.entity.animation.play('land_hard_main')

    def update(self, dt):
        self.entity.velocity[0] = 0

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('idle')


