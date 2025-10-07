import random
from .decision import Decision

class PatrolEndDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.reset_patrol_timer()

    def reset_patrol_timer(self):
        self.time_left = random.randint(*self.cfg['time_range'])

    def choose(self, player_distance, dt):
        results = []

        # Patrol timer countdown
        self.time_left -= dt
        if self.time_left <= 0:
            dir = random.choice([-1, 1])
            results.append(Decision(
                next_state="wait",
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs={"time": 50, "next_state": "patrol", "dir": dir}
            ))
            self.reset_patrol_timer()

        return results        