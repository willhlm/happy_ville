import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class SwordAir1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air1_main')}


class SwordAirMain(SwordAir):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)#animation name
        self.entity.sword.use_sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')#slash 1 and 2
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def increase_phase(self):
        self.enter_state('fall')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('run')
            else:
                self.enter_state('idle')


