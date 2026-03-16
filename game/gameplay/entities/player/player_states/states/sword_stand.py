from .base_composite import CompositeState
from .sword_base import Sword
from engine import constants as C

class SwordStand1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordStandMain(entity, animation_name = 'sword_stand1_main'), 'post': SwordStandPost(entity, animation_name = 'sword_stand1_post')}

class SwordStand2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordStandMain(entity, animation_name = 'sword_stand2_main'), 'post': SwordStandPost(entity, animation_name = 'sword_stand2_post')}

class SwordStandPre(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        self.enter_phase('main')

class SwordStandMain(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.sword.use_sword()
        self.entity.projectiles.add(self.entity.sword)

    def handle_movement(self, axes):
        value = axes.move
        if value[0] == 0:
            self.entity.acceleration[0] = 0

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        self.enter_phase('post')

class SwordStandPost(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')