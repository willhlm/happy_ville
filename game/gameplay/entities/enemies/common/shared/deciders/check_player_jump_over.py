from .decision import Decision

class CheckPlayerJumpOverDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs
        self.last_player_x_sign = None  # Track which side player was on (absolute)
        
    def choose(self, player_distance, dt):
        results = []
        
        player_x_diff = player_distance[0]
        player_y_diff = player_distance[1]
        
        # Check if player is above the entity
        is_above = player_y_diff < -10  # Adjust threshold as needed
        
        if is_above:
            # Determine which side player is on (regardless of entity facing direction)
            current_x_sign = 1 if player_x_diff > 0 else -1 if player_x_diff < 0 else 0
            
            # Detect if player crossed over (changed sides while airborne)
            if self.last_player_x_sign is not None and current_x_sign != 0:
                if self.last_player_x_sign != current_x_sign:
                    results.append(Decision(
                        next_state=self.cfg['next_state'],
                        score=self.cfg['score'],
                        priority=self.cfg['priority'],
                        kwargs=self.cfg['kwargs']
                    ))
            
            self.last_player_x_sign = current_x_sign
        else:
            # Reset when player lands
            self.last_player_x_sign = None
        
        return results