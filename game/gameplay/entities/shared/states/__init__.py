from .enemy.patrol import Patrol
from .enemy.chase import Chase
from .enemy.idle import Idle
from .enemy.wait import Wait
from .enemy.hurt import Hurt
from .enemy.death import Death
from .enemy.attack import AttackPre, AttackMain

SHARED_STATES = {
    'patrol': Patrol,
    'chase': Chase,
    'wait': Wait,
    'hurt': Hurt,
    'death': Death,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
}