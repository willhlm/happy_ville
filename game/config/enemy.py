"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'base': {
        'health': 4,
        'speeds': {'chase': 1, 'patrol': 0.5},
        'distances': {'aggro': [200, 20], 'attack': [50, 150], 'jump': [100, -10]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
            'jump_attack': [200, 250]#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max         

        'deciders': {
            'patrol': {
                    'check_player': {'next_state':'wait', 'score': 80, 'priority': 1, 'kwargs': {'time':10, 'next_state':'chase'}}, 
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}},
            'chase': {
                    'melee_attack': {'next_state':'attack_pre','score': 70, 'priority': 1, 'cooldown': 'melee_attack'}, 
                    'jump_attack': {'next_state':'jump_attack_pre', 'score': 40, 'priority': 1, 'cooldown': 'jump_attack'}, 
                    'chase_give_up': {'next_state':'wait','score':50,'priority':1,'give_up_time':400, 'kwargs': {'next_state':'patrol', 'time': 30}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}},
            'wait': {
                    'wait': {}},
        }
    }
}