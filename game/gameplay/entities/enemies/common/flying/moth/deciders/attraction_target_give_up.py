from gameplay.entities.enemies.common.shared.state_machine.deciders.decision import Decision
from gameplay.entities.enemies.common.shared.state_machine.deciders.config_utils import resolve_distance


class AttractionTargetGiveUpDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.give_up_time = self.cfg['give_up_time']
        self.giveup_timer = self.give_up_time
        self.aggro_distance = resolve_distance(entity, kwargs, 'aggro')

    def choose(self, player_distance, dt):
        target_distance = self.entity.currentstate.target_distance
        if abs(target_distance[0]) > self.aggro_distance[0] or abs(target_distance[1]) > self.aggro_distance[1]:
            self.giveup_timer -= dt
            if self.giveup_timer <= 0:
                return [Decision(
                    next_state=self.cfg['next_state'],
                    score=self.cfg['score'],
                    priority=self.cfg['priority'],
                    kwargs=self.cfg.get('kwargs', {}),
                )]
            return []

        self.giveup_timer = self.give_up_time
        return []
