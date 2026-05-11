"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'lyktgubbe': {
        'health': 4,
        'speeds': {'patrol': 0.5},
        'distances': {'aggro': [200, 20]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max         

        'states': {
            'wait': {},
            'hurt': {},
            'death': {},
            'dead': {},
            'patrol': {
                'deciders':{
                    'check_player': {'next_state':'wait', 'distance': 'aggro', 'score': 80, 'priority': 1, 'require_ground_path': True, 'kwargs': {'time':10, 'next_state':'attack_pre'}},#check if player in range and visible, if so attack
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'attack_pre': {},
            'attack_main': {
                'deciders':{
                    'chase_give_up': {'next_state':'attack_post', 'distance': 'aggro', 'score': 90, 'priority': 1, 'give_up_time': 100},#if player too far away for too long, give up and patrol                
                }
            },
            'attack_post': {},
        }
    }
}
