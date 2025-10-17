from gameplay.entities.shared.deciders.decision import Decision

class JumpAttackDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.dec_cfg = kwargs
        self.jump_distance = self.entity.config['distances']['jump']

    def choose(self, player_distance, dt):
        results = []
        if abs(player_distance[0]) < self.jump_distance[0] and player_distance[1] < self.jump_distance[1]:
            if self.entity.currentstate.cooldowns.get(self.dec_cfg['cooldown']) <= 0:
                results.append(Decision(
                    next_state=self.dec_cfg['next_state'],
                    score= self.dec_cfg['score'],
                    priority= self.dec_cfg['priority']
                ))

        return results