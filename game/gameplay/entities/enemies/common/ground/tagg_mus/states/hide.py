import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class HidePre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_pre")

    def increase_phase(self):
        self.enter_state("hide_main")

class HideMain(BaseState):
    def __init__(self, entity, deciders, config_key,**kwargs):
        super().__init__(entity, deciders,config_key)
        self.entity.animation.play("attack_main")

    def increase_phase(self):
        pass

    def modify_hit(self, effect):    
        copy_effect = effect.copy()
        copy_effect.damage = 0  
        return copy_effect        

class HidePost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")

    def increase_phase(self):
        self.enter_state("patrol")        
