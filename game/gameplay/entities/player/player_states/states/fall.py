from .base_composite import CompositeState
from .base_state import PhaseAirBase
from engine import constants as C


class FallState(CompositeState):
    AIR_GLIDE_GROUND_PROBE_DISTANCE = 12

    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {"pre": FallPre(entity), "main": FallMain(entity)}

    def common_values(self):
        self.falltime = 0

    def update(self, dt):
        self.falltime += dt
        self.current_phase.update(dt)

    def determine_fall(self):
        return self.falltime >= 4000

    def determine_sprint(self):
        return self.entity.flags["sprint_chain_active"]

    def can_double_jump(self):
        return self.entity.flags["double_jump_available"] and self.entity.abilities.is_unlocked("wind") and not self.entity.game_objects.physics.collision_queries.has_floor_below(self.entity, self.AIR_GLIDE_GROUND_PROBE_DISTANCE)

    def can_enter_air_glide(self):
        return self.entity.abilities.is_unlocked("shield") and not self.entity.game_objects.physics.collision_queries.has_floor_below(self.entity, self.AIR_GLIDE_GROUND_PROBE_DISTANCE)

class FallPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("fall_pre")

    def handle_press_input(self, input):
        if input.name == "jump":
            input.processed()
            if self.entity.flags["ground"]:  # cayote jump
                self.enter_state("jump")
            elif self.entity.currentstate.states["fall"].can_double_jump():
                self.enter_state("double_jump", phase="main")
            elif self.entity.currentstate.states["fall"].can_enter_air_glide():
                self.enter_state("air_glide")
        elif input.name == "ability":
            input.processed()
            self.do_ability()
        elif input.name == "dash":
            if self.entity.flags["ground"]:
                input.processed()
                self.enter_state("dash_ground")
            else:
                input.processed()
                self.enter_state("dash_air")
        elif input.name == "attack":
            input.processed()
            self.swing_sword("air")

    def handle_release_input(self, input):
        if input.name == "jump":
            input.processed()
        elif input.name == "dash":
            self.entity.flags["sprint_chain_active"] = False
            input.processed()

    def increase_phase(self):
        self.enter_phase("main")

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            should_sprint = (
                self.entity.game_objects.input_manager.is_held("gameplay", "dash")
                and self.entity.currentstate.states["fall"].determine_sprint()
            )
            self.entity.flags["sprint_chain_active"] = False
            if self.entity.currentstate.states["fall"].determine_fall():
                self.enter_state("land", phase="hard")
            elif should_sprint:
                self.enter_state("sprint")
            elif self.entity.acceleration[0] != 0:
                self.enter_state("run")
            else:
                self.enter_state("land", phase="soft")
            return

        if self.entity.has_wall_glide_collision():
            self.enter_state("wall_glide")


class FallMain(FallPre):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("fall_main")

    def increase_phase(self):
        pass
