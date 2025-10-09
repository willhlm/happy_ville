from gameplay.entities.shared.states.enemy.base_state import BaseState

class JumpBackPre(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("jump_back_pre")

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("jump_back_main")

class JumpBackMain(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("jump_back_main")
        self.entity.velocity[1] = -2
        self.time = 15  # sliding duration
        self.dir = functions.sign(self.player_distance[0])  # jump back opposite direction

    def update_logic(self, dt):
        self.entity.velocity[0] -= self.dir * 2
        self.time -= dt
        if self.time <= 0:
            self.enter_state("wait", time=40, next_state="chase")