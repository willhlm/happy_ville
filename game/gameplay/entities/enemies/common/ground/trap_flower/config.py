"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'trap_flower': {
        'health': 4,
        'initial_state': 'wait',
        'distances': {'attack': [50, 150]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max         

        'states': {
            'wait': {},
            'hurt': {},
            'death': {},
            'dead': {},
            'attack_pre': {},
            'attack_main': {},
            'attack_post': {},
        }
    }
}
