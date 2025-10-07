from .decision import Decision

class CheckPlayerDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) < self.entity.aggro_distance[0] and abs(player_distance[1]) < self.entity.aggro_distance[1]:
            results.append(Decision(
                next_state="wait",
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs={"time": self.cfg.get('time',10), "next_state": "chase"}
            ))

        return results