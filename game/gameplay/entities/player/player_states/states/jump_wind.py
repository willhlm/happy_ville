from .base_composite import CompositeState
from .base_state import PhaseAirBase
from engine import constants as C
from gameplay.entities.visuals.cosmetics import Dusts


class JumpWindState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {"main": JumpWindMain(entity),"post": JumpWindPost(entity)}

class JumpWindMain(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("jump_wind_main")
        if kwarg.get("double_jump", False):
            self.entity.flags["double_jump_available"] = False
        self.entity.audio.play("jump")
        self.entity.animation.frame = kwarg.get("frame", 0)
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_controller.start_double_jump(C.double_jump_boost)

    def update(self, dt):
        self.jump_dash_timer -= dt
        if self.entity.velocity[1] >= 0.7:
            self.enter_state("fall")

    def handle_press_input(self, input):
        if input.name == "dash":
            input.processed()
            self.entity.movement_controller.interrupt_jump()
            if self.jump_dash_timer > 0:
                self.entity.velocity[1] = 0
                self.enter_state("dash_jump")
            else:
                self.enter_state("dash_air")
        elif input.name == "attack":
            input.processed()
            self.swing_sword()
        elif input.name == "ability":
            input.processed()
            self.do_ability()
        elif input.name == "jump":
            input.processed()
            if self.entity.flags["bounce_jump"]:
                jump_boost = self.entity.consume_bounce_jump()
                self.entity.movement_controller.extend_jump(jump_boost=jump_boost, air_timer=C.air_timer)
                self.jump_dash_timer = max(self.jump_dash_timer, C.bounce_dash_jump_buffer_player)

    def handle_release_input(self, input):
        if input.name == "jump":
            input.processed()

    def swing_sword(self):
        if not self.entity.flags["attack_able"]:
            return
        if self.entity.dir[1] > C.down_angle:
            self.enter_state("sword_up")
        elif self.entity.dir[1] < C.down_angle * -1:
            self.enter_state("sword_down")
        else:
            state = "sword_air" + str(self.entity.combat_tracker.next_swing_index())
            self.enter_state(state)

    def consume_contact_state(self):
        if self.entity.has_collision_kind("belt"):
            self.entity.movement_controller.interrupt_jump()
            self.enter_state("wall_glide")

    def increase_phase(self):
        self.enter_phase("post")

class JumpWindPost(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("jump_wind_post")
        self.entity.audio.play("jump")
        self.entity.animation.frame = kwarg.get("frame", 0)
        self.jump_dash_timer = C.jump_dash_timer

    def update(self, dt):
        self.jump_dash_timer -= dt
        if self.entity.velocity[1] >= 0.7:
            self.enter_state("fall")

    def handle_press_input(self, input):
        if input.name == "dash":
            input.processed()
            self.entity.movement_controller.interrupt_jump()
            if self.jump_dash_timer > 0:
                self.entity.velocity[1] = 0
                self.enter_state("dash_jump")
            else:
                self.enter_state("dash_air")
        elif input.name == "attack":
            input.processed()
            self.swing_sword()
        elif input.name == "ability":
            input.processed()
            self.do_ability()
        elif input.name == "jump":
            input.processed()
            if self.entity.flags["bounce_jump"]:
                jump_boost = self.entity.consume_bounce_jump()
                self.entity.movement_controller.extend_jump(jump_boost=jump_boost, air_timer=C.air_timer)
                self.jump_dash_timer = max(self.jump_dash_timer, C.bounce_dash_jump_buffer_player)

    def handle_release_input(self, input):
        if input.name == "jump":
            input.processed()

    def swing_sword(self):
        if not self.entity.flags["attack_able"]:
            return
        if self.entity.dir[1] > C.down_angle:
            self.enter_state("sword_up")
        elif self.entity.dir[1] < C.down_angle * -1:
            self.enter_state("sword_down")
        else:
            state = "sword_air" + str(self.entity.combat_tracker.next_swing_index())
            self.enter_state(state)

    def consume_contact_state(self):
        if self.entity.has_collision_kind("belt"):
            self.entity.movement_controller.interrupt_jump()
            self.enter_state("wall_glide")
