from gameplay.entities.enemies.bosses.shared.utils import register_state

STATE_REGISTRY = {}


class BaseState:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def update(self, dt):
        pass

    def handle_input(self, input_type):
        if input_type == "hurt":
            self.entity.currentstate.clear_tasks()
            self.entity.currentstate.queue_task(task="hurt")
            self.entity.currentstate.start_next_task()

    def consume_contact_state(self):
        pass

    def increase_phase(self):
        pass

    def start_next_task(self):
        self.entity.currentstate.start_next_task()


@register_state(STATE_REGISTRY)
class Idle(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play(kwargs.get("animation", "idle"))


@register_state(STATE_REGISTRY)
class Wait(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("idle")
        self.duration = kwargs.get("duration", 30)

    def update(self, dt):
        self.entity.velocity[0] *= 0.8
        self.duration -= dt
        if self.duration <= 0:
            self.start_next_task()


@register_state(STATE_REGISTRY, name="turn_around")
class TurnAround(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.dir[0] *= -1
        self.entity.animation.play("idle")

    def update(self, dt):
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Think(BaseState):
    def update(self, dt):
        dist_x, _ = self.entity.currentstate.player_distance
        if (dist_x > 0 and self.entity.dir[0] == -1) or (dist_x < 0 and self.entity.dir[0] == 1):
            self.entity.currentstate.queue_task(task="wait", duration=12)
            self.entity.currentstate.queue_task(task="turn_around")
            self.entity.currentstate.queue_task(task="wait", duration=12)
            self.entity.currentstate.queue_task(task="think")
            self.start_next_task()
            return

        if self.entity.pending_phase_transition:
            self.entity.pending_phase_transition = False
            for task in self.entity.config["phase_transition_tasks"]:
                self.entity.currentstate.queue_task(**task)
            self.start_next_task()
            return

        if not self.entity.flags["attack_able"]:
            self.entity.currentstate.queue_task(task="wait", duration=18)
            self.entity.currentstate.queue_task(task="think")
            self.start_next_task()
            return

        pattern = self.entity.currentstate.selector.pick_pattern(*self.entity.currentstate.player_distance)
        for step in pattern["tasks"]:
            self.entity.currentstate.queue_task(**step)
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Walk(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("walk")
        self.duration = kwargs.get("duration", self.entity.config["walk_duration"])
        self.speed_multiplier = kwargs.get("speed_multiplier", 1.0)

    def update(self, dt):
        self.duration -= dt
        walk_speed = self.entity.config["walk_speed"] * self.speed_multiplier
        self.entity.velocity[0] = dt * self.entity.dir[0] * walk_speed

        dist_x = self.entity.currentstate.player_distance[0]
        if abs(dist_x) <= self.entity.config["walk_stop_distance"]:
            self.start_next_task()
            return

        if self.duration <= 0:
            self.start_next_task()

    def consume_contact_state(self):
        if self.entity.has_collision_kind("Wall"):
            self.entity.dir[0] *= -1


@register_state(STATE_REGISTRY, name="intro_fall")
class IntroFall(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("jump_main")
        self.left_ground = not self.entity.is_on_floor()

    def update(self, dt):
        self.entity.velocity[0] = 0

        if not self.left_ground and not self.entity.is_on_floor():
            self.left_ground = True
            return

        if self.left_ground and self.entity.is_on_floor():
            self.start_next_task()


@register_state(STATE_REGISTRY, name="roar_pre")
class RoarPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roar_pre")

    def increase_phase(self):
        self.start_next_task()

    def handle_input(self, input_type):
        pass


@register_state(STATE_REGISTRY, name="roar_main")
class RoarMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roar_main")
        self.entity.game_objects.camera_manager.camera_shake(amp=3, duration=100)
        center = [
            self.entity.rect.centerx - self.entity.game_objects.camera_manager.camera.scroll[0],
            self.entity.rect.centery - self.entity.game_objects.camera_manager.camera.scroll[1],
        ]
        self.entity.game_objects.post_process.append_shader("Speed_lines", center=center)
        self.cycles = 7

    def handle_input(self, input_type):
        pass

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles <= 0:
            self.entity.game_objects.post_process.remove_shader("Speed_lines")
            self.start_next_task()

@register_state(STATE_REGISTRY, name="roar_post")
class RoarPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roar_post")

    def increase_phase(self):
        self.start_next_task()

    def handle_input(self, input_type):
        pass

@register_state(STATE_REGISTRY, name="lick_pre")
class LickPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.flags["attack_able"] = False
        self.entity.animation.play("lick_pre")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="lick_main")
class LickMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("lick_main")
        self.entity.lick_attack()
        self.entity.start_attack_cooldown("lick")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="spit_pre")
class SpitPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.flags["attack_able"] = False
        self.entity.animation.play("spit_pre")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="spit_main")
class SpitMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("spit_main")
        self.entity.spit_attack()
        self.entity.start_attack_cooldown("spit")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="jump_pre")
class JumpPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("jump_pre")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="jump_main")
class JumpMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("jump_main")
        self.entity.velocity[1] = -self.entity.config["jump_velocity"]
        self.left_ground = not self.entity.is_on_floor()

    def update(self, dt):
        self.entity.velocity[0] = dt * self.entity.dir[0] * self.entity.config["jump_speed"]
        if not self.left_ground:
            if not self.entity.is_on_floor():
                self.left_ground = True
            return

        if self.entity.velocity[1] >= 0:
            self.start_next_task()

    def consume_contact_state(self):
        if self.entity.has_collision_kind("Wall"):
            self.entity.dir[0] *= -1


@register_state(STATE_REGISTRY, name="fall")
class Fall(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play('fall_main')

    def update(self, dt):
        self.entity.velocity[0] = dt * self.entity.dir[0] * self.entity.config["jump_speed"]

    def consume_contact_state(self):
        if self.entity.has_collision_kind("Wall"):
            self.entity.dir[0] *= -1

        if self.entity.is_on_floor():
            self.start_next_task()


@register_state(STATE_REGISTRY)
class Land(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("land")
        self.entity.game_objects.camera_manager.camera_shake(amplitude=10, duration=25, scale=0.98)

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Hurt(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("hurt")
        self.entity.flags["hurt_state_able"] = False
        self.entity.game_objects.timer_manager.start_timer(
            self.entity.config["hurt_recovery"],
            self.entity.on_hurt_timeout,
        )

    def update(self, dt):
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        if self.entity.pending_phase_transition:
            self.entity.pending_phase_transition = False
            for task in self.entity.config["phase_transition_tasks"]:
                self.entity.currentstate.queue_task(**task)
        else:
            self.entity.currentstate.queue_task(task="wait", duration=12)
            self.entity.currentstate.queue_task(task="think")
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Death(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("death")

    def update(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.entity.currentstate.queue_task(task="dead")
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Dead(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("dead")
        self.entity.dead()
