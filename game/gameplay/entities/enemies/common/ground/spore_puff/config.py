"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'spore_puff': {
        'health': 4,
        'speeds': {'patrol': 0.5},

        'initial_state': 'patrol',
        'distances': {'aggro': [50, 150]},#x, y
        'cooldowns': {
            'melee_attack': [200, 300],#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max         

        'states': {
            'wait': {},
            'hurt': {},
            'death': {},
            'dead': {},
            'patrol': {
                'deciders':{
                    'melee_attack': {'next_state': 'attack_pre', 'distance': 'aggro', 'score': 80, 'priority': 1, 'cooldown': 'melee_attack'},
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'attack_pre': {},
            'attack_main': {},
            'attack_post': {},
        }
    }
}
