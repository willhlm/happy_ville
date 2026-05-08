import math


def move_towards(entity, target, dt, speed):
    dx = target[0] - entity.hitbox.centerx
    dy = target[1] - entity.hitbox.centery
    distance = math.hypot(dx, dy)
    if distance <= 0.001:
        return 0

    entity.velocity[0] += dt * (dx / distance) * speed
    entity.velocity[1] += dt * (dy / distance) * speed
    return distance
