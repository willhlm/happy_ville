import math

from .base_composite import CompositeState
from .base_state import PhaseBase
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.entities.visuals.cosmetics import ThunderSpark

class ThunderState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {"pre": ThunderPre(entity), "main": ThunderMain(entity), "post": ThunderPost(entity)}

class ThunderPre(PhaseBase):
    AIM_TIME_SCALE = 0.2

    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.ability = self.entity.abilities.get("thunder")
        self.duration = 100
        self.slow_motion = self.entity.game_objects.time_manager.modify_time(time_scale=self.AIM_TIME_SCALE, duration=float('inf'))
        self.arrow = self.entity.game_objects.ui.hud.widgets.show_point_arrow("thunder", self.entity.rect.topleft, [0, -1])

    def update(self, dt):
        self.duration -= dt / self.AIM_TIME_SCALE
        self.arrow.set_pos(self.entity.rect.topleft)
        if self.duration < 0:
            self.exit_state()

    def exit(self):
        self.entity.game_objects.time_manager.remove_modifier(self.slow_motion)
        self.entity.shader_state.enter_state("Idle")
        self.entity.game_objects.ui.hud.widgets.hide("thunder")

    def exit_state(self):
        aim_dir = self.ability.get_dive_direction([self.arrow.dir[0], -self.arrow.dir[1]])
        if self.ability.find_surface(aim_dir) is None:
            self.enter_state("idle" if self.entity.is_on_floor() else "fall")
            return
        self.exit()
        self.enter_phase("main", dir=aim_dir)

    def handle_release_input(self, input):
        if input.name == "ability":
            input.processed()
            self.exit_state()

    def handle_movement(self, axes):
        value = axes.move
        if value[0] != 0 or value[1] != 0:
            self.arrow.dir = [value[0], -value[1]]


class ThunderMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("thunder_main")
        direction = kwarg.get("dir", [0, 1])
        length = math.hypot(*direction)
        self.dir = [value / length for value in direction]
        ability = self.entity.abilities.get("thunder")
        distance = ability.get_surface_radius() + 1
        self.time = distance / ability.traverse_speed
        self.previous_acceleration = self.entity.acceleration[0]
        self.entity.acceleration[0] = 0
        self.entity.end_coyote_time()
        self.entity.movement_modifier.add_modifier(
            "transport", authoritative=True, entity=self.entity, direction=self.dir,
            speed=ability.traverse_speed, distance=distance,
        )
        self.entity.flags["invincibility"] = True
        self.entity.shader_state.add_shader("mb")

    def update(self, dt):
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha=100))
        self.time -= dt
        if self.time <= 0:
            self.enter_state("idle" if self.entity.is_on_floor() else "fall")

    def exit(self):
        self.entity.movement_modifier.remove_modifier("transport")
        self.entity.acceleration[0] = self.previous_acceleration
        self.entity.velocity = [0, 0]
        self.entity.flags["invincibility"] = False
        self.entity.shader_state.remove_shader("mb")
        self.entity.shader_state.enter_state("Idle")

    def exit_state(self):
        self.exit()
        self.enter_phase("post", dir=self.dir)

    def handle_movement(self, event):
        pass

    def consume_contact_state(self):
        if any(c.normal[0] * self.dir[0] + c.normal[1] * self.dir[1] < 0 for c in self.entity.contact_state.collisions):
            self.exit_state()

class ThunderPost(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play("thunder_post")
        self.entity.flags["invincibility"] = True
        self.entity.game_objects.time_manager.modify_time(time_scale = 0, duration =7, callback =lambda: self.entity.game_objects.camera_manager.camera_shake(amplitude=20, duration=30, scale=0.96))
        sparks = ThunderSpark(self.entity.rect.topleft, self.entity.game_objects)
        sparks.rect.midbottom = [
            self.entity.hitbox.midbottom[0],
            self.entity.hitbox.midbottom[1] + 16,
        ]
        self.entity.game_objects.cosmetics.add(sparks)

    def update(self, dt):
        self.entity.velocity = [0, 0]

    def handle_movement(self, event):
        pass

    def exit(self):
        self.entity.flags["invincibility"] = False

    def increase_phase(self):
        self.enter_state("idle" if self.entity.is_on_floor() else "fall")
