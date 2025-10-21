from .decision import Decision

class CheckCollisionsDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.directions = kwargs.get('directions', [])
        
    def choose(self, player_distance, dt):
        results = []        
        for direction in self.directions:
            if self.entity.collision_types[direction]:
                return results.append(Decision(
                    next_state=self.cfg['next_state'],
                    score=self.cfg['score'],
                    priority=self.cfg['priority'],
                    kwargs=self.cfg.get('kwargs', {})
                ))

        return results