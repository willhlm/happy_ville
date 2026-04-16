def find_closest_in_direction(current_container, containers, direction):
    if not current_container:
        return None

    current = current_container.rect
    best = None
    best_score = float('inf')

    for container in containers:
        if container == current_container:
            continue

        target = container.rect
        dx = target.centerx - current.centerx
        dy = target.centery - current.centery

        if direction == 'up' and dy >= 0:
            continue
        if direction == 'down' and dy <= 0:
            continue
        if direction == 'left' and dx >= 0:
            continue
        if direction == 'right' and dx <= 0:
            continue

        distance = dx ** 2 + dy ** 2
        angle_priority = abs(dx if direction in ('up', 'down') else dy)
        score = distance + angle_priority * 0.5

        if score < best_score:
            best_score = score
            best = container

    return best
