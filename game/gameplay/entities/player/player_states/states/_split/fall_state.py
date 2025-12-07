import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class FallState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': FallPre(entity), 'main': FallMain(entity)}

    def enter_state(self, phase_name, **kwarg):
        super().enter_state(phase_name, **kwarg)
        self.allow_sprint = kwarg.get('allow_sprint', False)

    def common_values(self):#call when this state is enetred
        self.falltime = 0

    def update(self, dt):
        self.falltime += dt

    def determine_fall(self):
        if self.falltime >= 4000: return True
        return False

    def determine_sprint(self):
        return self.allow_sprint


class FallPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_pre')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('jump', air_timer = self.entity.colliding_platform.jumped())
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='lb':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('dash_ground')
            else:
                input.processed()
                self.enter_state('dash_air')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_input(self, input, **kwarg):
        if input == 'Wall':
            self.enter_state('wall_glide', **kwarg)
        elif input == 'belt':
            self.enter_state('belt_glide')
        elif input == 'Ground':
            if self.entity.currentstate.states['fall'].determine_fall():
                self.enter_state('land', phase = 'hard')
            elif self.entity.game_objects.controller.is_held('lb') and self.entity.currentstate.states['fall'].determine_sprint():
                self.enter_state('sprint')
            else:
                if self.entity.acceleration[0] != 0:
                    self.enter_state('run')#enter run pre phase
                else:
                    self.enter_state('land', phase = 'soft')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('sword_down')
        else:#right or left
            state = 'sword_air' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_phase('main')


class FallMain(FallPre):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_main')

    def increase_phase(self):#called when an animation is finihed for that state
        pass


