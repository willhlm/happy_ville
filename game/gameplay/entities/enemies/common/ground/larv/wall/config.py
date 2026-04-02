ENEMY_CONFIG = {
    'larv_wall': {
        'health': 3,
        'initial_state': 'crawl',
        'friction': [0.1, 0.1],
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
        },
        'states': {
            'crawl': {},
            'hurt': {},
            'death': {},
            'dead': {},
            'wait': {},
        },
    }
}
