"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'hedge': {
        'health': 4,
        'speeds': {'chase': 0.5},
        'distances': {'aggro': [200, 30]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
            'jump_attack': [50, 80]#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max         
        'initial_state': 'sleep',   
        'deciders': {
            'sleep': { 'check_player': {'next_state':'wake_up', 'score': 80, 'priority': 1, 'kwargs': {'time':10, 'next_state':'chase'}}},
            'chase': {
                    'check_player_jump_over': {'next_state':'wait', 'score': 80, 'priority': 2, 'kwargs': {'time':40, 'next_state':'chase','dir': -1}},
                    'chase_give_up': {'next_state':'wait','score':50,'priority':1,'give_up_time':400, 'kwargs': {'next_state':'sleep', 'time': 30}}, 
                    'check_edge': {'next_state':'sleep', 'score':90, 'priority':2}},
            'wait': {
                    'wait': {}},
        }
    }
}