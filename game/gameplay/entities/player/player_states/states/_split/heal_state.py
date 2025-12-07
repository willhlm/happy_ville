import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class HealState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': HealPre(entity), 'main': HealMain(entity)}


class HealPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('heal_pre')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1] == 'rt':#if releasing the button
            input.processed()
            self.enter_state('idle')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_phase('main')


class HealMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('heal_main')
        self.heal_cost = 1

    def handle_release_input(self, input):
        event = input.output()
        if event[-1] == 'rt':#if releasing the button
            input.processed()
            self.enter_state('idle')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.entity.heal()
        self.entity.backpack.inventory.remove('amber_droplet', self.heal_cost)
        self.enter_state('Heal_main')


