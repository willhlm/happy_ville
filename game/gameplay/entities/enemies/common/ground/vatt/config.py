"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'vatt': {
        'health': 1,
        'speeds': {'patrol': 0.3, 'skip': 0.5},
        'distances': {},  # x, y
        'cooldowns': {},
        'timers': {'hurt_recovery': [200, 250]},  # min max         
        
        'states': {
            'wait': {},
            'hurt': {},
            'death': {},
            'dead': {},
            'patrol': {
                'deciders':{
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'skip', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'skip': {
                'deciders':{
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [80, 150], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge_skip': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },            
        }
    }
}
