from .idle import Idle
from .wait import Wait
from .hurt import Hurt
from .death import Death
from .attack import AttackPre, AttackMain

from .ground.patrol import GroundPatrol
from .ground.chase import GroundChase

from .flying.patrol import FlyingPatrol
from .flying.chase import FlyingChase

SHARED_STATES = {
    'ground': {
        'patrol': GroundPatrol,
        'chase': GroundChase,
        'wait': Wait,
        'hurt': Hurt,
        'death': Death,
        'attack_pre': AttackPre,
        'attack_main': AttackMain,
    },
    'flying':{
        'patrol': FlyingPatrol,
        'chase': FlyingChase,
        'wait': Wait,
        'hurt': Hurt,
        'death': Death,
        'attack_pre': AttackPre,
        'attack_main': AttackMain,        
    }
}