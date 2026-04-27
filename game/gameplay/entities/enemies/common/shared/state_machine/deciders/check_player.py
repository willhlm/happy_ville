from .decision import Decision
from .config_utils import resolve_distance

class CheckPlayerDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.aggro_distance = resolve_distance(entity, kwargs, 'aggro')
        self.require_ground_path = kwargs.get('require_ground_path', False)
        self.ground_probe_step = kwargs.get('ground_probe_step', 16)
        self.ground_probe_depth = kwargs.get('ground_probe_depth', 5)

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) < self.aggro_distance[0] and abs(player_distance[1]) < self.aggro_distance[1]:
            if self.require_ground_path and not self._has_ground_path_to_player(player_distance):
                return results

            results.append(Decision(
                next_state=self.cfg['next_state'],
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs=self.cfg.get('kwargs', {})
            ))

        return results

    def _has_ground_path_to_player(self, player_distance):
        if player_distance[0] == 0:
            return True

        collision_queries = self.entity.game_objects.physics.collision_queries
        probe_y = self.entity.hitbox.bottom + self.ground_probe_depth
        start_x = self.entity.hitbox.centerx
        end_x = self.entity.hitbox.centerx + player_distance[0]

        step = self.ground_probe_step if end_x >= start_x else -self.ground_probe_step
        x = start_x

        while (x <= end_x) if step > 0 else (x >= end_x):
            if not collision_queries.check_ground([x, probe_y]):
                return False
            x += step

        return collision_queries.check_ground([end_x, probe_y])
