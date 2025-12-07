import random, math

from .base_composite import CompositeState
from .base_state import PhaseBase, PhaseAirBase
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class ThunderState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': ThunderPre(entity), 'main': ThunderMain(entity), 'post': ThunderPost(entity)}


class ThunderPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        #self.entity.animation.play('thunder_pre')
        self.ball = ThunderBall(self.entity.rect.topleft, self.entity.game_objects)#will be aila since aila will be swirlying
        self.entity.game_objects.cosmetics.add(self.ball)

        self.duration = 100
        self.entity.shader_state.enter_state('Swirl')#take current animation and swirl it

        if self.entity.abilities.spirit_abilities['Thunder'].level == 2:#aim arrow
            self.arrow = PointArrow(self.entity.rect.topleft, self.entity.game_objects)
            self.entity.game_objects.cosmetics.add(self.arrow)

    def update(self, dt):
        self.duration -= dt
        self.entity.velocity = [0, 0]

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.entity.shader_state.enter_state('Idle')
        self.ball.kill()
        if self.entity.abilities.spirit_abilities['Thunder'].level == 1:
            self.enter_phase('main', dir = [0,1])
        else:
            self.arrow.kill()
            self.enter_phase('main', dir = [self.arrow.dir[0],-self.arrow.dir[1]])

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='b':
            input.processed()
            self.exit_state()

    def handle_movement(self, event):
        if self.entity.abilities.spirit_abilities['Thunder'].level == 2:
            value = event['l_stick']#the avlue of the press
            if value[0] != 0 or value[1] != 0:
                self.arrow.dir = [value[0],-value[1]]


class ThunderMain(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('thunder_main')
        self.dir = kwarg.get('dir', [0, 1])
        self.time = 30#how long to thunder dive
        self.entity.flags['invincibility'] = True
        self.entity.shader_state.enter_state('MB')

    def update(self, dt):
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.entity.velocity = [20*self.dir[0], 20*self.dir[1]]
        self.time -= dt
        if self.time < 0:
            self.exit_state()

    def exit_state(self):
        self.entity.shader_state.enter_state('Idle')
        self.enter_phase('post')

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input in ['Ground', 'Wall', 'belt']:
            self.exit_state()


class ThunderPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('thunder_post')
        self.entity.game_objects.time_manager.modify_time(time_scale = 0, duration = 7, callback = lambda: self.entity.game_objects.camera_manager.camera_shake(amplitude = 30, duration = 30, scale = 0.9))#freeze

        sparks = ThunderSpark(self.entity.rect.topleft, self.entity.game_objects)
        sparks.rect.midbottom = [self.entity.hitbox.midbottom[0], self.entity.hitbox.midbottom[1] + 16]#adjust the position
        self.entity.game_objects.cosmetics.add(sparks)

    def update(self, dt):
        self.entity.velocity = [0,0]

    def handle_movement(self, event):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        self.entity.flags['invincibility'] = False
        self.enter_state('idle')


