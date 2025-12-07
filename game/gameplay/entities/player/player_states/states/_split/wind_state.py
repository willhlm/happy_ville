import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class WindState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WindMain(entity)}


class WindMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self):
        self.entity.animation.play('wind_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Wind'].initiate()

    def increase_phase(self):
        self.enter_state('idle')


