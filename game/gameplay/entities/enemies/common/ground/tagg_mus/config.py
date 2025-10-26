"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'base': {
        'health': 4,
        'speeds': {'chase': 0.8, 'patrol': 0.5},
        'distances': {'aggro': [200, 20], 'attack': [50, 150]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max         

        'states': {
            'patrol': {
                'deciders':{
                    'check_player': {'next_state':'wait', 'score': 80, 'priority': 1, 'kwargs': {'time':10, 'next_state':'hide_pre'}}, 
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'hide_main': {
                'deciders':{
                    'check_safe': {'next_state':'hide_post', 'score': 80, 'priority': 1, 'kwargs': {}}, 
                    },
            },
        }
    }
}