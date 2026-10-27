from gameplay.entities.enemies.bosses.shared.utils import register_state


STATE_REGISTRY = {}


class BaseState:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def update(self, dt):
        pass

    def handle_input(self, input_type):
        if input_type != "hurt":
            return
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
        self.entity.velocity[0] = 0
        self.entity.animation.play("idle")


@register_state(STATE_REGISTRY)
class Wait(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.velocity[0] = 0
        self.entity.animation.play("idle")
        self.duration = kwargs.get("duration", 30)

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.start_next_task()


@register_state(STATE_REGISTRY)
class Roar(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.velocity[0] = 0
        self.entity.animation.play("roar")
        self.entity.roar_effect.start(
            amplitude=3,
            duration=35,
            scale=0.95,
        )

    def increase_phase(self):
        self.start_next_task()

    def exit(self):
        self.entity.roar_effect.stop()


@register_state(STATE_REGISTRY)
class Think(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.velocity[0] = 0
        self.entity.animation.play("idle")

    def update(self, dt):
        pattern = self.entity.currentstate.selector.pick_pattern(
            *self.entity.currentstate.player_distance
        )
        for step in pattern["tasks"]:
            self.entity.currentstate.queue_task(**step)
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Hurt(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.velocity[0] = 0
        self.entity.animation.play("hurt")
        self.entity.flags["hurt_state_able"] = False
        self.entity.game_objects.timer_manager.start_timer(
            self.entity.config["hurt_recovery"],
            self.entity.on_hurt_timeout,
        )

    def increase_phase(self):
        self.entity.currentstate.queue_task(task="think")
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Death(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.velocity = [0, 0]
        self.entity.animation.play("hurt")

    def increase_phase(self):
        self.entity.currentstate.queue_task(task="dead")
        self.start_next_task()


@register_state(STATE_REGISTRY)
class Dead(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity, **kwargs)
        self.entity.animation.play("idle")
        self.entity.dead()
