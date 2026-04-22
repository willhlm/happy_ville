from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Crawl(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.set_surface_motion_paused(False)
        self.entity.animation.play('walk', 0.18)

    def update_logic(self, dt):
        self.entity.update_surface_crawl_state(dt, self.player_distance)
