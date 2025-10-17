from gameplay.entities.shared.deciders.decision import Decision

class CheckSafeDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.aggro_distance = entity.config['distances']['aggro']

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) > self.aggro_distance[0] and abs(player_distance[1]) > self.aggro_distance[1]:
            results.append(Decision(
                next_state=self.cfg['next_state'],
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs=self.cfg['kwargs']
            ))

        return results