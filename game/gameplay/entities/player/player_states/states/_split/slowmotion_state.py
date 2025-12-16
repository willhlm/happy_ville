import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class SlowMotionState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SlowMotionPre(entity), 'main': SlowMotionMain(entity)}


class SlowMotionPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.acceleration[0] = 0#stop moving
        self.entity.animation.play('slow_motion_pre')

    def increase_phase(self):
        self.enter_phase('main')


class SlowMotionMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.animation.play('slow_motion_main')
        self.entity.abilities.spirit_abilities['Slow_motion'].initiate()

    def increase_phase(self):
        self.enter_state('idle')


