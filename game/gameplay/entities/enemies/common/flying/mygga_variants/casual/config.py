ENEMY_CONFIG = {
    'mygga': {
        'health': 3,
        'speeds': {'patrol': 0.1},
        'timers': {'hurt_recovery': [150, 200]},
        
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
                    }                    
                }
            },
        }
    }
}