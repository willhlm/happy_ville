from .decision import Decision

class ChaseGiveUpDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.giveup_timer = self.cfg['time']

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) > self.entity.aggro_distance[0] or abs(player_distance[1]) > self.entity.aggro_distance[1]:
            self.giveup_timer -= dt
            if self.giveup_timer <= 0:
                results.append(Decision(
                    next_state="wait",
                    score=self.cfg['score'],
                    priority=self.cfg['priority'],
                    kwargs={"time": self.cfg.get('wait_time', 20), "next_state": self.cfg['next_state']}
                ))
        else:
            self.giveup_timer = self.cfg['time']

        return results