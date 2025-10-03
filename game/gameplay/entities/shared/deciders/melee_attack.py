from .decision import Decision

class MeleeAttackDecider():
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.dec_cfg = kwargs

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) < self.entity.attack_distance[0]:
            if self.entity.currentstate.cooldowns.get(self.dec_cfg['cooldown']) <= 0:
                results.append(Decision(
                    next_state="attack_pre",
                    score=self.dec_cfg['score'],
                    priority=self.dec_cfg['priority']
                ))

        return results