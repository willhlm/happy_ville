import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class DeathState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DeathPre(entity), 'main': DeathMain(entity), 'post': DeathPost(entity)}


class DeathPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)
        self.timeout = 50

    def enter(self, **kwarg):
        self.entity.animation.play('death_pre')
        self.entity.game_objects.cosmetics.add(PlayerSoul([self.entity.rect[0],self.entity.rect[1]],self.entity.game_objects))

    def update(self, dt):
        self.timeout -= dt
        self.entity.acceleration[0] = 0#slow down
        self.entity.invincibile = True
        if self.timeout < 0:
            self.enter_phase('main')

    def handle_movement(self,event):
        pass

    def handle_input(self, input):
        if input == 'Ground' or input == 'hole':
            self.enter_phase('main')


class DeathMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('death_main')

    def update(self, dt):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_phase('post')


class DeathPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.dead()
        self.entity.animation.play('death_post')

    def update(self, dt):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass


