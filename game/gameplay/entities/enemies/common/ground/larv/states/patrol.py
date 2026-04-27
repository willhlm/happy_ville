import random

from .crawl import Crawl


class Patrol(Crawl):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key, **kwargs)
        self.patrol_time = 0

    def update_logic(self, dt):
        super().update_logic(dt)

        if self.patrol_time <= 0:
            patrol_cfg = self.entity.config['patrol']
            self.patrol_time = random.randint(patrol_cfg['crawl_time'][0], patrol_cfg['crawl_time'][1])

        self.patrol_time -= dt
        if self.patrol_time > 0:
            return

        patrol_cfg = self.entity.config['patrol']
        wait_cfg = patrol_cfg['wait_time']
        turn = random.random() < patrol_cfg.get('turn_chance', 1)
        self.enter_state('wait', time = random.randint(wait_cfg[0], wait_cfg[1]), next_state = 'patrol', turn = turn)
