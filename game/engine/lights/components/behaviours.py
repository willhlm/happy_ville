import math
import random


class LightBehaviour:
    component_type = None

    def update(self, light, dt):
        raise NotImplementedError


class FlickerBehaviour(LightBehaviour):
    component_type = "flicker"

    def __init__(self, amount=0.1):
        self.amount = amount

    def update(self, light, dt):
        alpha = light.colour[-1] + random.uniform(-self.amount, self.amount)
        light.colour[-1] = max(0.0, min(1.0, alpha))


class FadeBehaviour(LightBehaviour):
    component_type = "fade"

    def __init__(self, rate=0.99):
        self.rate = rate

    def update(self, light, dt):
        light.colour[-1] *= self.rate


class PulsatingBehaviour(LightBehaviour):
    component_type = "pulsating"

    def __init__(self, speed=0.01):
        self.speed = speed
        self.time = 0

    def update(self, light, dt):
        self.time += dt * self.speed
        radius = 0.5 * light.init_radius * math.sin(self.time) + light.init_radius * 0.5
        light.set_radius(radius)


class ExpandBehaviour(LightBehaviour):
    component_type = "expand"

    def __init__(self, speed=None):
        self.speed = speed

    def update(self, light, dt):
        expand_speed = light.expand_speed if self.speed is None else self.speed
        light.set_radius(min(light.radius + dt * expand_speed, light.max_radius))


class LifetimeBehaviour(LightBehaviour):
    component_type = "lifetime"

    def __init__(self, time):
        self.remaining = time

    def update(self, light, dt):
        self.remaining -= dt
        if self.remaining <= 0:
            light.kill()


LIGHT_BEHAVIOURS = {
    "flicker": FlickerBehaviour,
    "fade": FadeBehaviour,
    "pulsating": PulsatingBehaviour,
    "expand": ExpandBehaviour,
    "lifetime": LifetimeBehaviour,
}


def build_component(component_type, **kwargs):
    component_cls = LIGHT_BEHAVIOURS[component_type]
    return component_cls(**kwargs)
