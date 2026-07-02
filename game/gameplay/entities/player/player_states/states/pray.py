import random
from .base_composite import CompositeState
from .base_state import PhaseBase
from gameplay.entities.visuals.cosmetics import PrayEffect


class PrayState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': PrayPre(entity), 'main': PrayMain(entity), 'post': PrayPost(entity)}

class PrayPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('pray_pre')
        self.entity.acceleration[0] = 0
        effect = PrayEffect(self.entity.rect.center, self.entity.game_objects)
        effect.rect.bottom = self.entity.rect.bottom
        self.entity.game_objects.cosmetics.add(effect)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['pray'][0])

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_phase('main')

class PrayMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('pray_main')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_phase('post')

class PrayPost(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('pray_post')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_state('idle')
