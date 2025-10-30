ENEMY_CONFIG = {
    'mygga': {
        'health': 3,
        'speeds': {'patrol': 0.1, 'chase': 0.6},
        'distances': {'aggro': [180,130], 'attack': [150,100]},

        'timers': {'hurt_recovery': [150, 200]},
        'cooldowns': {'melee_attack': [150, 250]},#min max        
        'states': {
            'patrol': {
                'deciders': {
                    'patrol_position_end': {
                        'next_state': 'wait',
                        'score': 80,
                        'priority': 1,
                        'kwargs': {'time': 20, 'next_state': 'patrol'}
                    },
                    'check_collisions': {
                        'next_state': 'wait',
                        'directions': ['left', 'right', 'top', 'bottom'],
                        'score': 80,
                        'priority': 1,
                        'kwargs': {'time': 20, 'next_state': 'patrol'}
                    },
                    'check_player': {'next_state':'wait', 'score': 80, 'priority': 1, 'kwargs': {'time':10, 'next_state':'chase'}},                    
                }
            },
            'chase': {
                'deciders':{
                    'melee_attack': {'next_state': 'attack_pre','score': 70, 'priority': 1, 'cooldown': 'melee_attack'}, 
                    'chase_give_up': {'next_state':'wait','score':50,'priority':1,'give_up_time':400, 'kwargs': {'next_state':'patrol', 'time': 30}}, 
                    },
            },                     
        }
    }
}