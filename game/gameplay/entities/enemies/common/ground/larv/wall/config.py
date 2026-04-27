ENEMY_CONFIG = {
    'larv_wall': {
        'health': 3,
        'initial_state': 'crawl',
        'speeds': {
            'crawl': 1.2,
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
        'states': {
            'crawl': {
                'deciders': {
                    'surface_edge': {
                        'next_state': 'wait',
                        'score': 90,
                        'priority': 2,
                        'reasons': ['unsupported_surface'],
                        'lookahead': 8,
                        'kwargs': {'time': 35, 'next_state': 'crawl', 'turn': True},
                    },
                },
            },
            'fall': {},
            'land': {
                'kwargs': {
                    'next_state': 'wait',
                    'next_state_kwargs': {'next_state': 'crawl','time': 150},
                },
            },
            'hurt': {
                'next_state': 'crawl',
            },
            'death': {},
            'dead': {},
            'wait': {},
        },
    }
}
