from .decision import Decision


class ChaseStuckDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.stuck_timer = 0
        self.stuck_time = kwargs.get('stuck_time', 45)
        self.min_progress = kwargs.get('min_progress', 2)
        self.min_player_distance = kwargs.get('min_player_distance', 24)
        self.require_wall_collision = kwargs.get('require_wall_collision', True)
        self.previous_x = entity.hitbox.centerx

    def choose(self, player_distance, dt):
        results = []
        current_x = self.entity.hitbox.centerx
        progress = abs(current_x - self.previous_x)
        self.previous_x = current_x

        if self._is_stuck(player_distance, progress):
            self.stuck_timer += dt
            if self.stuck_timer >= self.stuck_time:
                results.append(Decision(
                    next_state=self.cfg['next_state'],
                    score=self.cfg['score'],
                    priority=self.cfg['priority'],
                    kwargs=self.cfg.get('kwargs', {})
                ))
        else:
            self.stuck_timer = 0

        return results

    def _is_stuck(self, player_distance, progress):
        player_dx = player_distance[0]
        facing_x = self.entity.dir[0]

        if facing_x == 0:
            return False

        if abs(player_dx) < self.min_player_distance:
            return False

        if player_dx * facing_x <= 0:
            return False

        if progress >= self.min_progress:
            return False

        if not self.require_wall_collision:
            return True

        blocking_side = 'right' if facing_x > 0 else 'left'
        return self.entity.has_collision_side(blocking_side)
