import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class JumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': JumpMain(entity)}


class JumpMain(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_main')#the name of the class
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['jump'][random.randint(0,2)], vol = 0.1)
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.jump_dash_timer = C.jump_dash_timer
        #self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.flags['ground'] = False
        self.shroomboost = 1#if landing on shroompoline and press jump, this vakue is modified

        self.air_timer = kwarg.get('air_timer', 10)
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'two'))#dust

    def update(self, dt):
        self.jump_dash_timer -= dt
        self.air_timer -= dt
        if self.air_timer >= 0:
            self.entity.velocity[1] = C.jump_vel_player * self.shroomboost
        if self.entity.velocity[1] >= 0.7:
            self.enter_state('fall')#pre

    def handle_press_input(self,input):
        event = input.output()
        if event[-1]=='lb':
            input.processed()
            if self.jump_dash_timer > 0:
                self.entity.velocity[1] = 0
                self.enter_state('dash_jump')
            else:
                self.enter_state('dash_air')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='a':
            input.processed()
            if self.entity.flags['shroompoline']:
                self.shroomboost = 2

    def handle_release_input(self,input):#when release space
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.entity.velocity[1] = 0.5*self.entity.velocity[1]
            self.enter_state('fall')#pre

    def handle_input(self, input, **kwarg):
        if input == 'belt':
            self.enter_state('belt_glide')

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


