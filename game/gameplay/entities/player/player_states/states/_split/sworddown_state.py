import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class SwordDownState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordDownMain(entity)}


class SwordDownMain(SwordAir):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sword_down_main')
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()
        self.entity.sword.currentstate.enter_state('Slash_down')
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def increase_phase(self):
        self.enter_state('fall')


