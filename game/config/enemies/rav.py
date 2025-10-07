"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'rav': {
        'health': 4,
        'speeds': {'chase': 1, 'patrol': 0.5},
        'distances': {'aggro': [200, 20], 'attack': [50, 150], 'jump': [100, -10]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max
            'jump_attack': [50, 80]#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max

        'deciders': {
            'patrol': {
                    'check_player': {'score': 80, 'priority': 1}, 
                    'patrol_end': {'score':50,'priority':0,'time_range':[80,220]}, 
                    'check_edge': {'score':90, 'priority':2, 'time':60, 'next_state':'patrol', 'dir':-1}},
            'chase': {
                    'melee_attack': {'score': 40, 'priority': 1, 'cooldown': 'melee_attack'}, 
                    'jump_attack': {'score': 80, 'priority': 1, 'cooldown': 'jump_attack'}, 
                    'chase_give_up': {'score':50,'priority':1,'time':400,'next_state':'patrol'}, 
                    'check_edge': {'score':90, 'priority':2, 'time':60, 'next_state':'patrol', 'dir':-1}},
            'wait': {
                    'wait': {}},
        }

    }
}