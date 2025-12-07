import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class ReSpawnState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': ReSpawnMain(entity)}


class ReSpawnMain(PhaseBase):#enters when aila respawn after death
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('respawn')
        self.entity.invincibile = False

    def handle_movement(self,event):
        pass

    def increase_phase(self):#when animation finishes
        self.entity.health = max(self.entity.health,0)#if negative, set it to 0
        self.entity.heal(self.entity.max_health)
        if self.entity.backpack.map.spawn_point.get('bone', False):#if bone, remove it
            self.entity.backpack.map.spawn_point.pop()
        self.enter_state('idle')


