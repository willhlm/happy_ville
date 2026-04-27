from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class Land(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.next_state = kwargs.get('next_state', 'crawl')
        self.next_state_kwargs = kwargs.get('next_state_kwargs', {})

        self.entity.surface_stick_physics.set_enabled(True)
        self.entity.velocity = [0, 0]
        self.entity.animation.play(kwargs.get('animation', 'idle'), 0.18)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state(self.next_state, **self.next_state_kwargs)
