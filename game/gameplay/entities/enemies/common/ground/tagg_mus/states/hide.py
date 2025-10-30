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
        self.entity.hit_component.damage_manager.add_modifier('super_armor')
        self.entity.material = 'metal'

    def increase_phase(self):
        pass    

class HidePost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")
        self.entity.hit_component.damage_manager.remove_modifier('super_armor')
        self.entity.material = 'flesh'

    def increase_phase(self):
        self.enter_state("patrol")        
