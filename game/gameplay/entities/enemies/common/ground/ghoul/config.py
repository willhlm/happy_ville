"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'ghoul': {
        'health': 1,
        'speeds': {'patrol': 0.5},
        'distances': {'aggro': [200, 40], 'attack': [50, 20]},#x, y
        'cooldowns': {
            'melee_attack': [150, 250],#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max

        'initial_state': 'invisible',

        'states': {
            'invisible': {
                'deciders':{
                    'check_player': {'next_state': 'spawn', 'score': 80, 'priority': 1},
                    },
            },
            'spawn': {},
            'wait': {},
            'hurt': {'next_state': 'wait', 'kwargs': {'time':100, 'next_state': 'patrol'}},
            'death': {},
            'patrol': {
                'deciders':{
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}},
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'attack_pre': {},
            'attack_main': {'kwargs': {'next_state': 'patrol'}},
        }
    }
}
