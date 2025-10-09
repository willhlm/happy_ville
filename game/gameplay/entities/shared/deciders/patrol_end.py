import random
from .decision import Decision

class PatrolEndDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.reset_patrol_timer()

    def reset_patrol_timer(self):
        self.time_left = random.randint(*self.cfg['patrol_time'])

    def choose(self, player_distance, dt):
        results = []

        # Patrol timer countdown
        self.time_left -= dt
        if self.time_left <= 0:
            dir = random.choice([-1, 1])
            results.append(Decision(
                next_state=self.cfg['next_state'],
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs=self.cfg.get('kwargs', {})
            ))
            self.reset_patrol_timer()

        return results        