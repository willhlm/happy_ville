from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Crawl(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('walk', 0.18)

    def consume_contact_state(self):
        if not self.entity.surface_stick_physics.is_enabled():
            return
        if self.entity.surface_stick_physics.has_surface():
            return

        self.enter_state('fall')

    def update_logic(self, dt):
        self.entity.apply_surface_move_velocity()
