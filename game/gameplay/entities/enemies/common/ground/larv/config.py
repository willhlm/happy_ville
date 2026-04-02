ENEMY_CONFIG = {
    'larv': {
        'health': 3,
        'initial_state': 'patrol',
        'speeds': {
            'patrol': 0.5,
            'ground_snap': 0.2,
        },
        'timers': {
            'hurt_recovery': [200, 250],
            'hang_drop_delay': 12,
        },
        'hanging': {
            'sway_speed': [0.018, 0.03],
            'sway_x': [1.5, 4.0],
            'sway_y': [1.0, 2.5],
        },
        'states': {
            'hanging': {},
            'dropping': {},
            'land': {},
            'hurt': {
                'next_state': 'wait',
                'kwargs': {'time': 50, 'next_state': 'patrol'}
            },
            'patrol': {
                'deciders': {
                    'patrol_end': {
                        'next_state': 'wait',
                        'score': 50,
                        'priority': 0,
                        'patrol_time': [150, 200],
                        'kwargs': {'next_state': 'patrol', 'time': 50}
                    },
                    'check_edge': {
                        'next_state': 'wait',
                        'score': 90,
                        'priority': 2,
                        'kwargs': {'time': 60, 'next_state': 'patrol', 'dir': -1}
                    }
                },
            },
        }
    }
}
