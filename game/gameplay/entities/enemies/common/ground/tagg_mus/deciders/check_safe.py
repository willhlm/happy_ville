from gameplay.entities.enemies.common.shared.state_machine.deciders.decision import Decision
from gameplay.entities.enemies.common.shared.state_machine.deciders.config_utils import resolve_distance

class CheckSafeDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.aggro_distance = resolve_distance(entity, kwargs, 'aggro')

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) > self.aggro_distance[0] and abs(player_distance[1]) > self.aggro_distance[1]:
            results.append(Decision(
                next_state=self.cfg['next_state'],
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs=self.cfg.get('kwargs', {})
            ))

        return results
