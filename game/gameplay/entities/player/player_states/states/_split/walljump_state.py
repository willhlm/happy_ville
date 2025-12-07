import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class WallJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallJumpMain(entity)}#'pre': WallJumpPre(entity),


class WallJumpMain(JumpMain):
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)

    def enter(self, **kwarg):
        super().enter(**kwarg)
        self.entity.animation.play('wall_jump_main')#the name of the class
        self.entity.velocity[0] = -self.entity.dir[0]*6
        self.ignore_input_timer = 8
        self.accelerate_timer = 15
        self.start_dir = -kwarg.get('wall_dir', [1,0])[0]
        self.entity.dir[0] = self.start_dir
        #self.entity.dir[0] =

    def update(self, dt):
        super().update(dt)
        self.ignore_input_timer -= 1
        self.accelerate_timer -= 1

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        super().handle_movement(event)
        if self.ignore_input_timer > 0:
            self.entity.dir[0] = self.start_dir
        if self.accelerate_timer > 0:
            self.entity.acceleration[0] = C.acceleration[0]


