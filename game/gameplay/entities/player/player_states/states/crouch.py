import random
from .base_composite import CompositeState
from .base_state import PhaseBase
from gameplay.entities.visuals.cosmetics import PrayEffect


class CrouchState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': CrouchPre(entity), 'main': CrouchMain(entity), 'post': CrouchPost(entity)}

class CrouchPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('crouch_pre')
        self.entity.acceleration[0] = 0
        effect = PrayEffect(self.entity.rect.center, self.entity.game_objects)
        effect.rect.bottom = self.entity.rect.bottom
        self.entity.game_objects.cosmetics.add(effect)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['pray'][0])

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_phase('main')

class CrouchMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)
        self.animation_number = 1

    def enter(self, **kwarg):
        self.entity.animation.play('crouch1_main')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        if random.randint(0, self.animation_number * 2) == 0:
            self.animation_number = 3 - self.animation_number
            animation_name = 'crouch' + str(self.animation_number) + '_main'
            self.entity.animation.play(animation_name)

    def handle_input(self, input, **kwarg):
        if input == 'pray_post':
            self.enter_phase('post')

class CrouchPost(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('crouch_post')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_state('idle')