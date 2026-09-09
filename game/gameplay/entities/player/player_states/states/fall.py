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
        self.jump_decision_timer = 0
        self.jump_decision_pending = False

    def begin_jump_decision(self):
        self.jump_decision_timer = 0
        self.jump_decision_pending = True

    def update(self, dt):
        self.falltime += dt
        self.current_phase.update(dt)
        self.jump_decision_timer += dt
        if self.jump_decision_timer >= C.air_jump_grace_timer:
            if self.entity.game_objects.input_manager.is_held("gameplay", "jump") and self.can_enter_air_glide():
                self.entity.currentstate.enter_state("air_glide")

    def release_jump_decision(self):
        if not self.jump_decision_pending:
            return
        self.jump_decision_pending = False
        if self.jump_decision_timer < C.air_jump_grace_timer and self.entity.flags["double_jump_available"] and self.entity.abilities.is_unlocked("wind"):
            self.entity.currentstate.enter_state("jump_wind", phase="main", double_jump=True)

    def determine_fall(self):
        return self.falltime >= 4000

    def determine_sprint(self):
        return self.entity.flags["sprint_chain_active"]

    def can_enter_air_glide(self):
        return self.entity.abilities.is_unlocked("shield") and not self.entity.game_objects.physics.collision_queries.has_floor_below(self.entity, self.AIR_GLIDE_GROUND_PROBE_DISTANCE)        

class FallPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("fall_pre")

    def handle_press_input(self, input):
        if input.name == "jump":
            if self.entity.flags["ground"]:  # cayote jump
                input.processed()
                self.enter_state("jump")
            else:
                input.processed()
                self.entity.currentstate.states["fall"].begin_jump_decision()
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
            self.swing_sword()

    def handle_release_input(self, input):
        if input.name == "jump":
            input.processed()
            self.entity.currentstate.states["fall"].release_jump_decision()
        elif input.name == "dash":
            self.entity.flags["sprint_chain_active"] = False
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
