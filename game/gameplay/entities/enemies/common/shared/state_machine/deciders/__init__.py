from .chase_give_up import ChaseGiveUpDecider
from .check_edge import CheckEdgeDecider
from .patrol_end import PatrolEndDecider
from .melee_attack import MeleeAttackDecider
from .check_player import CheckPlayerDecider
from .check_player_jump_over import CheckPlayerJumpOverDecider
from .patrol_position_end import PatrolPositionEndDecider
from .check_collisions import CheckCollisionsDecider

SHARED_DECIDERS = {
    "melee_attack": MeleeAttackDecider,    
    "chase_give_up": ChaseGiveUpDecider,
    "check_edge": CheckEdgeDecider,
    'check_player': CheckPlayerDecider,
    'patrol_end': PatrolEndDecider,
    "check_player_jump_over": CheckPlayerJumpOverDecider, 
    'patrol_position_end': PatrolPositionEndDecider,
    'check_collisions': CheckCollisionsDecider,

}