import random

from gameplay.entities.enemies.bosses.shared.utils import register_state

STATE_REGISTRY = {}


class BaseState:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def update(self, dt):
        pass

    def handle_input(self, input_type):
        if input_type == "hurt":
            return

    def consume_contact_state(self):
        pass

    def increase_phase(self):
        pass

    def start_next_task(self):
        self.entity.currentstate.start_next_task()

    def enter_state(self, state_name, **kwargs):
        self.entity.currentstate.clear_tasks()
        self.entity.currentstate.queue_task(task=state_name, **kwargs)
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

        if not self.entity.flags["attack_able"]:
            self.entity.currentstate.queue_task(task="wait", duration=18)
            self.entity.currentstate.queue_task(task="think")
            self.start_next_task()
            return

        pattern = self.entity.currentstate.selector.pick_pattern(*self.entity.currentstate.player_distance)
        if pattern is None:
            self.entity.currentstate.queue_task(task="wait", duration=18)
            self.entity.currentstate.queue_task(task="think")
            self.start_next_task()
            return

        for step in pattern["tasks"]:
            self.entity.currentstate.queue_task(**step)
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Walk(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("walk")
        self.duration = kwargs.get("duration", self.entity.config["walk_duration"])

    def update(self, dt):
        self.duration -= dt
        self.entity.velocity[0] = dt * self.entity.dir[0] * self.entity.config["walk_speed"]

        if abs(self.entity.currentstate.player_distance[0]) <= self.entity.attack_distance[0]:
            self.start_next_task()
            return

        if self.duration <= 0:
            self.start_next_task()

    def consume_contact_state(self):
        if self.entity.has_collision_kind("Wall"):
            self.entity.dir[0] *= -1


@register_state(STATE_REGISTRY, name="sleep_main")
class SleepMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.spatial_emitter_id = self.entity.game_objects.sound.register_spatial_point(
            self.entity.sounds["sleeping"][0],
            get_point=lambda: self.entity.hitbox.center,
            base_volume=1,
            loops=-1,
            min_dist=48,
            max_dist=500,
        )
        self.entity.animation.play("sleep_main")

    def handle_input(self, input_type):
        if input_type != "hurt":
            return
        if self.entity.ID and not self.entity.game_objects.world_state.narrative.is_flow_complete(self.entity.ID):
            self.entity.start_encounter_sequence()
            return
        self.entity.start_wake_intro()


@register_state(STATE_REGISTRY, name="sleep_post")
class SleepPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("sleep_post")
        self.entity.game_objects.sound.unregister_emitter(self.entity.spatial_emitter_id)

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="roar_pre")
class RoarPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roar_pre")

    def increase_phase(self):
        self.start_next_task()


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
        self.entity.game_objects.sound.play_sfx(self.entity.sounds["roar"][0], vol=0.8)
        self.cycles = 20

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles < 0:
            self.entity.game_objects.post_process.remove_shader("Speed_lines")
            self.start_next_task()


@register_state(STATE_REGISTRY, name="roar_post")
class RoarPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roar_post")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="attack_pre")
class AttackPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("attack_pre")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="attack_main")
class AttackMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("attack_main")
        self.entity.attack()
        self.entity.set_cooldown("melee_attack")
        self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds["attack"]), vol=0.8)

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="attack_post")
class AttackPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("attack_post")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="slam_pre")
class SlamPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("slam_pre")
        self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds["slam"]), vol=0.8)

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="slam_main")
class SlamMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("slam_main")
        self.entity.slam()
        self.entity.set_cooldown("slam_attack")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="slam_post")
class SlamPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("slam_post")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="roll_attack_pre")
class RollAttackPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roll_attack_pre")

    def increase_phase(self):
        self.start_next_task()


@register_state(STATE_REGISTRY, name="roll_attack_main")
class RollAttackMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roll_attack_main")
        self.entity.velocity[1] = -5
        self.dir = self.entity.dir.copy()
        self.number_bounce = 5
        self.request_bounce = False

    def update(self, dt):
        self.entity.velocity[0] += self.dir[0] * 2
        if self.request_bounce:
            self.entity.velocity[1] = -8
            self.request_bounce = False

    def handle_input(self, input_type):
        pass

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            self.request_bounce = True
            self.number_bounce -= 1
            if self.number_bounce <= 0:
                self.start_next_task()

        if self.entity.is_on_ceiling():
            self.dir[1] = 1

        if self.entity.has_collision_kind("Wall"):
            if self.entity.is_on_wall_side("left"):
                self.dir[0] = 1
            else:
                self.dir[0] = -1


@register_state(STATE_REGISTRY, name="roll_attack_post")
class RollAttackPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("roll_attack_post")
        self.entity.set_cooldown("roll_attack")

    def increase_phase(self):
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
