import random
from .decision import Decision

class PatrolPositionEndDecider():#checks if target position is reached
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs

    def choose(self, player_distance, dt):
        target_position = self.entity.currentstate.state.target_position
        if (abs(target_position[0] - self.entity.rect.centerx) < 10 and abs(target_position[1] - self.entity.rect.centery) < 10):#if reached target                     
            return [Decision(
                next_state=self.cfg['next_state'],
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                kwargs = self.cfg['kwargs']
            )]
        
        return []        