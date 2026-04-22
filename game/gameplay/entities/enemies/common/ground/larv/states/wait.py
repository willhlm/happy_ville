from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Wait(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        self.wait_time = kwargs.get('time', 35)
        self.next_state = kwargs.get('next_state', 'crawl')
        self.turn = kwargs.get('turn', False)
        super().__init__(entity, deciders, config_key)
        self.entity.set_surface_motion_paused(True)
        self.entity.animation.play("idle", 0.2)

    def update(self, dt):
        self.wait_time -= dt
        if self.wait_time <= 0:
            if self.turn:
                self.entity.reverse_surface_direction()
            self.enter_state(self.next_state)

    def update_logic(self, dt):
        pass

    def handle_input(self, input_type):
        if input_type == "Hurt":
            self.enter_state('hurt')
