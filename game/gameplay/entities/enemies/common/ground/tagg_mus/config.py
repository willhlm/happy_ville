"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'base': {
        'health': 2,
        'speeds': {'chase': 0.8, 'patrol': 0.5, 'retreat': 0.8},
        'distances': {'aggro': [200, 20], 'attack': [50, 150]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
            'tagg_burst_repeat': [200, 250],
        },
        'timers': {
            'hurt_recovery': [160, 210],
            'retreat_after_burst': [55, 85],
        },#min max

        'attacks': {
            'tagg_burst': {
                'counts': [8, 10],
                'speed': [3, 4],
                'lifetime': 120,
                'spawn_radius': 12,
                'angle_start_degrees': 135,
                'angle_end_degrees': 45,
            },
        },
        'states': {
            'wait': {},
            'death': {},
            'dead': {},
            'hurt': {},
            'patrol': {
                'deciders':{
                    'check_player_attack_ready': {'next_state':'wait', 'score': 80, 'priority': 1, 'kwargs': {'time':10, 'next_state':'attack_pre'}}, 
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'attack_pre': {},
            'attack_main': {
                'deciders':{
                    'check_safe': {'next_state':'attack_post', 'score': 80, 'priority': 1, 'kwargs': {}}, 
                    },
            },
            'attack_post': {},
            'retreat': {},
        }
    }
}
