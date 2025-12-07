import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class BowState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BowPre(entity), 'main': BowMain(entity)}

class BowPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self):
        self.entity.animation.play('bow_pre')
        self.duration = 100#charge times
        self.arrow = PointArrow(self.entity.rect.topleft, self.entity.game_objects, dir = self.entity.dir.copy())
        self.entity.game_objects.cosmetics.add(self.arrow)
        self.time = 0

    def update(self, dt):
        self.duration -= dt
        self.time += dt
        self.entity.velocity = [0, 0]

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.arrow.kill()
        self.enter_phase('main', dir = [self.arrow.dir[0], -self.arrow.dir[1]], time = self.time)

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='b':
            input.processed()
            self.exit_state()

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        if value[0] != 0 or value[1] != 0:
            self.arrow.dir = [value[0],-value[1]]


class BowMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('bow_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Bow'].initiate(dir = kwarg['dir'], time = kwarg['time'])

    def increase_phase(self):
        self.enter_state('idle')


