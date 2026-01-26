import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class SleepMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("sleep_main")

    def handle_input(self, input):   
        if input == 'Hurt':
            self.enter_state("sleep_post")

class SleepPost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("sleep_post")
        self.entity.game_objects.signals.emit('miniboss')

    def increase_phase(self):
        self.enter_state("roar_pre")