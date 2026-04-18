import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class SleepMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.spatial_emitter_id = self.entity.game_objects.sound.register_spatial_point(self.entity.sounds['sleeping'][0], get_point=lambda: self.entity.hitbox.center, base_volume=1, loops=-1, min_dist=48, max_dist=500)        
        self.entity.animation.play("sleep_main")

    def handle_input(self, input):   
        if input == 'Hurt':
            self.enter_state("sleep_post")

class SleepPost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("sleep_post")
        self.entity.game_objects.signals.emit('miniboss')
        self.entity.game_objects.sound.unregister_emitter(self.entity.spatial_emitter_id)

    def increase_phase(self):
        self.enter_state("roar_pre")