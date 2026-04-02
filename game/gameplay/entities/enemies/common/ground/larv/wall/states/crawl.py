from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Crawl(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self._sync_animation()

    def update_logic(self, dt):
        self._sync_animation()

    def _sync_animation(self):
        animation = 'idle'
        speed = 0.18
        if self.entity.animation.animation_name != animation:
            self.entity.animation.play(animation, speed)
