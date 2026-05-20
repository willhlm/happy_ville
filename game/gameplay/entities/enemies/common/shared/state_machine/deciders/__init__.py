from .chase_give_up import ChaseGiveUpDecider
from .chase_stuck import ChaseStuckDecider
from .check_edge import CheckEdgeDecider
from .patrol_end import PatrolEndDecider
from .melee_attack import MeleeAttackDecider
from .check_player import CheckPlayerDecider
from .check_player_jump_over import CheckPlayerJumpOverDecider
from .patrol_position_end import PatrolPositionEndDecider
from .check_collisions import CheckCollisionsDecider
from .surface_edge import SurfaceEdgeDecider
from .surface_land import SurfaceLandDecider

SHARED_DECIDERS = {
    "melee_attack": MeleeAttackDecider,    
    "chase_give_up": ChaseGiveUpDecider,
    "chase_stuck": ChaseStuckDecider,
    "check_edge": CheckEdgeDecider,
    'check_player': CheckPlayerDecider,
    'patrol_end': PatrolEndDecider,
    "check_player_jump_over": CheckPlayerJumpOverDecider, 
    'patrol_position_end': PatrolPositionEndDecider,
    'check_collisions': CheckCollisionsDecider,
    'surface_edge': SurfaceEdgeDecider,
    'surface_land': SurfaceLandDecider,
}
