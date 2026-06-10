ENEMY_CONFIG = {
    'crab_crystal': {
        'health': 3,
        'initial_state': 'patrol',
        'speeds': {
            'crawl': 0.5,
            'ground_snap': 0.2,
        },
        'timers': {
            'hurt_recovery': [200, 250],
        },
        'movement': {
            'stick_speed': 1.5,
            'probe_distance': 2,
            'corner_inset': 3,
            'surface_edge_lookahead': 8,
        },
        'patrol': {
            'crawl_time': [120, 200],
            'wait_time': [30, 55],
            'turn_chance': 0.5,
        },
        'states': {
            'patrol': {
                'deciders': {
                    'surface_edge': {
                        'next_state': 'wait',
                        'score': 90,
                        'priority': 2,
                        'reasons': ['unsupported_surface'],
                        'lookahead': 8,
                        'kwargs': {'time': 45, 'next_state': 'patrol', 'turn': True},
                    },
                },
            },
            'fall': {},
            'land': {
                'kwargs': {
                    'next_state': 'wait',
                    'next_state_kwargs': {'next_state': 'patrol', 'time': 10},
                },
            },
            'wait': {},
            'hurt': {
                'next_state': 'patrol',
            },
        }
    },
}
