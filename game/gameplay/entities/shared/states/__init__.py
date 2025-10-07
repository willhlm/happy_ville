from .patrol import Patrol
from .chase import Chase
from .idle import Idle
from .wait import Wait
from .hurt import Hurt
from .death import Death
from .attack import AttackPre, AttackMain

SHARED_STATES = {
    'patrol': Patrol,
    'chase': Chase,
    'wait': Wait,
    'hurt': Hurt,
    'death': Death,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
}