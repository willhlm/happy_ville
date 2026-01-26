"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'bjorn': {
        'health': 4,
        'speeds': {'chase': 0.9, 'patrol': 0.5},
        'distances': {'aggro': [200, 20], 'attack': [50, 150], 'roll': [100, 200], 'slam': [50, 150]},#x, y
        'cooldowns': {
            'melee_attack': [50, 80],#min max            
            'slam_attack': [50, 80],#min max
            'roll_attack': [200, 250]#min max
        },
        'timers': {'hurt_recovery': [200, 250]},#min max     
        'initial_state': 'sleep_main',

        'states': {
            'patrol': {
                'deciders':{
                    'check_player': {'next_state':'wait', 'score': 80, 'priority': 1, 'kwargs': {'time':10, 'next_state':'chase'}}, 
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
            'chase': {
                'deciders':{
                    'melee_attack': {'next_state':'attack_pre','score': 70, 'priority': 1, 'cooldown': 'melee_attack'}, 
                    'slam_attack': {'next_state':'slam_pre','score': 70, 'priority': 1, 'cooldown': 'slam_attack'}, 
                    'roll_attack': {'next_state':'roll_attack_pre', 'score': 40, 'priority': 1, 'cooldown': 'roll_attack'}, 
                    'chase_give_up': {'next_state':'wait','score':50,'priority':1,'give_up_time':400, 'kwargs': {'next_state':'patrol', 'time': 30}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },                                            
        }
    }
}