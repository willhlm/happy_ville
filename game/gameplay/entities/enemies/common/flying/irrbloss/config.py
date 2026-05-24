ENEMY_CONFIG = {
    'irrbloss': {
        'health': 2,
        'speeds': {
            'patrol': 0.1,
            'torpedo': 7.2,
        },
        'attack': {
            'charge_up_time': 60,
            'torpedo_time': 50,
        },
        'timers': {'hurt_recovery': [150, 200]},
        
        'states': {
            'wait': {},
            'death': {},
            'transform': {},
            'charge_up': {},
            'torpedo': {},
            'dead': {},
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
                    }                    
                }
            },
        }
    }
}
