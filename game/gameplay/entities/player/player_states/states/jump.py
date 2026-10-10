from .base_composite import CompositeState
from .base_state import PhaseAirBase
from engine import constants as C
from gameplay.entities.visuals.cosmetics import Dusts


class JumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {"main": JumpMain(entity)}


class JumpMain(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("jump_main")
        self.entity.audio.play("jump")
        self.entity.animation.frame = kwarg.get("frame", 0)
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_controller.start_jump(
            jump_boost=kwarg.get("jump_boost", 1),
            air_timer=kwarg.get("air_timer", C.air_timer),
        )
        self.entity.game_objects.cosmetics_fg.add(
            Dusts(
                self.entity.hitbox.center,
                self.entity.game_objects,
                dir=self.entity.dir,
                state="two",
            )
        )

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
            self.swing_sword("air")
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
            self.entity.movement_controller.release_jump()
            self.enter_state("fall")

    def consume_contact_state(self):
        if self.entity.has_collision_kind("belt"):
            self.entity.movement_controller.interrupt_jump()
            self.enter_state("wall_glide")
