import random
from gameplay.entities.shared.states.enemy.base_state import BaseState

class HidePre(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("attack_pre")

    def increase_phase(self):
        self.enter_state("hide_main")

class HideMain(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("attack_main")
        self.entity.attack()

    def increase_phase(self):
        pass

class HidePost(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("attack_post")

    def increase_phase(self):
        self.enter_state("patrol")        
