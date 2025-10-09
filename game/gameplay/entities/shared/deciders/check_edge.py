from .decision import Decision

class CheckEdgeDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs

    def choose(self, player_distance, dt):
        results = []        
        x = self.entity.hitbox.centerx + self.entity.dir[0] * (self.entity.hitbox.width // 2 + 5)
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision(
                next_state=self.cfg['next_state'],
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs=self.cfg.get('kwargs', {})
            ))

        return results