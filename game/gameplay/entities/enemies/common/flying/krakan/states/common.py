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


def steer_towards(entity, target, dt, speed, response = 0.42, slow_radius = 10):
    dx = target[0] - entity.hitbox.centerx
    dy = target[1] - entity.hitbox.centery
    distance = math.hypot(dx, dy)
    if distance <= 0.001:
        entity.velocity[0] *= 0.96
        entity.velocity[1] *= 0.96
        return 0

    desired_speed = speed * min(1, distance / slow_radius)
    desired_velocity = [
        (dx / distance) * desired_speed,
        (dy / distance) * desired_speed,
    ]
    blend = min(1, response * dt)
    entity.velocity[0] += (desired_velocity[0] - entity.velocity[0]) * blend
    entity.velocity[1] += (desired_velocity[1] - entity.velocity[1]) * blend
    return distance


def player_in_range(state, aggro_distance):
    return (
        abs(state.player_distance[0]) < aggro_distance[0]
        and abs(state.player_distance[1]) < aggro_distance[1]
    )


def player_in_home_zone(state, home_radius):
    player = state.entity.game_objects.player.hitbox
    return (
        abs(player.centerx - state.entity.original_pos[0]) < home_radius[0]
        and abs(player.centery - state.entity.original_pos[1]) < home_radius[1]
    )
