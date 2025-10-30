# orthogonal_torpedo/deciders/torpedo_attack.py
from gameplay.entities.enemies.common.shared.deciders.decision import Decision

class TorpedoAttackDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.horizontal_tolerance = 30
        
    def choose(self, player_distance, dt):
        # Only attack if positioned above player
        if (abs(player_distance[0]) < self.horizontal_tolerance and 
            player_distance[1] > 50):  # Player is below us
            
            if self.entity.currentstate.cooldowns.get(self.cfg['cooldown']) <= 0:
                return [Decision(
                    next_state=self.cfg['next_state'],
                    score=self.cfg['score'],
                    priority=self.cfg['priority']
                )]
        return []