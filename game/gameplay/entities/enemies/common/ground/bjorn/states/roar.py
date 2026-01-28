from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class RoarPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("roar_pre")   

    def increase_phase(self):
        self.enter_state('roar_main')

class RoarMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("roar_main")

        self.entity.game_objects.camera_manager.camera_shake(amp = 3, duration = 100)#amplitude, duration
        center = [self.entity.rect.centerx-self.entity.game_objects.camera_manager.camera.scroll[0],self.entity.rect.centery-self.entity.game_objects.camera_manager.camera.scroll[1]]
        self.entity.game_objects.post_process.append_shader('Speed_lines', center = center)    

        self.cycles = 14   

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles < 0:
            self.entity.game_objects.post_process.remove_shader('Speed_lines')
            self.enter_state('roar_post')

class RoarPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("roar_post")

    def increase_phase(self):
        self.enter_state('chase')            