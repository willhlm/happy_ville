from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Fall(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.surface_stick_physics.set_enabled(False)
        self.entity.animation.play(kwargs.get("animation", "idle"), 0.18)

    def update_logic(self, dt):
        pass

    def consume_contact_state(self):
        collision = self.entity.contact_state.surface_collision
        if collision is None:
            return
        if not self.entity.surface_stick_physics.attach_from_collision(collision):
            return

        self.entity.angle = self.entity.surface_stick_physics.get_angle()
        self.entity.surface_stick_physics.set_enabled(True)
        self.enter_state("land")
