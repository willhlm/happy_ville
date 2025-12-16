import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class IdleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': IdleMain(entity)}


class IdleMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('idle', f_rate = 0.1667)
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
        elif event[-1] == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()

        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()
        elif event[-1]=='rt':#depends on if the abillities have pre or main animation
            input.processed()
            self.enter_state('heal')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_movement(self, event):
        super().handle_movement(event)
        if abs(self.entity.acceleration[0]) > 0.5:
            self.enter_state('run')
        elif abs(self.entity.acceleration[0]) > 0.1:
            self.enter_state('walk')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] == 0:
            state = 'sword_stand' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0:
            self.enter_state('sword_up')


