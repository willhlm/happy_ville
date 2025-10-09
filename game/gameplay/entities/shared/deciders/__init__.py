from .chase_give_up import ChaseGiveUpDecider
from .check_edge import CheckEdgeDecider
from .wait import WaitDecider
from .patrol_end import PatrolEndDecider
from .melee_attack import MeleeAttackDecider
from .check_player import CheckPlayerDecider
from .check_player_jump_over import CheckPlayerJumpOverDecider

SHARED_DECIDERS = {
    "melee_attack": MeleeAttackDecider,    
    "chase_give_up": ChaseGiveUpDecider,
    "check_edge": CheckEdgeDecider,
    'check_player': CheckPlayerDecider,
    'patrol_end': PatrolEndDecider,
    "wait": WaitDecider,    
    "check_player_jump_over": CheckPlayerJumpOverDecider,    
}