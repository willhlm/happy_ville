import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class ShieldState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': ShieldPre(entity), 'main': ShieldMain(entity)}


class ShieldPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.acceleration[0] = 0#stop moving
        self.entity.animation.play('shield_pre')

    def increase_phase(self):
        self.enter_phase('main')


class ShieldMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.animation.play('shield_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Shield'].initiate()

    def increase_phase(self):
        self.enter_state('idle')


