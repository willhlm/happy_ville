from .decision import Decision

class ChaseGiveUpDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.giveup_timer = self.cfg['give_up_time']

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) > self.entity.aggro_distance[0] or abs(player_distance[1]) > self.entity.aggro_distance[1]:
            self.giveup_timer -= dt
            if self.giveup_timer <= 0:
                results.append(Decision(
                    next_state=self.cfg['next_state'],
                    score=self.cfg['score'],
                    priority=self.cfg['priority'],
                    kwargs=self.cfg['kwargs']
                ))
        else:
            self.giveup_timer = self.cfg['give_up_time']

        return results