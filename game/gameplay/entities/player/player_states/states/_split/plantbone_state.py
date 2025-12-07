import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class PlantBoneState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': PlantBoneMain(entity)}


class PlantBoneMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('plant_bone_main')
        self.entity.acceleration[0] = 0

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('idle')

#abilities

