ENEMY_CONFIG = {
    'larv': {
        'health': 3,
        'initial_state': 'crawl',
        'speeds': {
            'crawl': 0.5,
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
        'movement': {
            'stick_speed': 1.5,
            'probe_distance': 2,
            'corner_inset': 3,
        },
        'patrol': {
            'crawl_time': [120, 200],
            'wait_time': [30, 55],
        },
        'states': {
            'crawl': {},
            'hanging': {},
            'dropping': {},
            'land': {},
            'wait': {},
            'hurt': {
                'next_state': 'crawl',
            },
        }
    },
    'larv_poison': {
        'health': 3,
        'initial_state': 'crawl',
        'speeds': {
            'crawl': 0.4,
            'ground_snap': 0.2,
        },
        'timers': {
            'hurt_recovery': [200, 250],
            'hang_drop_delay': 12,
        },
        'cooldowns': {
            'surface_attack': [90, 130],
        },
        'distances': {
            'aggro': [220, 180],
            'attack': [190, 160],
        },
        'hanging': {
            'sway_speed': [0.018, 0.03],
            'sway_x': [1.5, 4.0],
            'sway_y': [1.0, 2.5],
        },
        'movement': {
            'stick_speed': 1.5,
            'probe_distance': 2,
            'corner_inset': 3,
        },
        'states': {
            'crawl': {},
            'hanging': {},
            'dropping': {},
            'land': {},
            'wait': {},
            'hurt': {
                'next_state': 'crawl',
            },
            'attack_pre': {},
            'attack_main': {},
        }
    },
    'larv_jr': {
        'health': 3,
        'initial_state': 'crawl',
        'speeds': {
            'crawl': 0.7,
        },
        'timers': {
            'hurt_recovery': [200, 250],
        },
        'movement': {
            'stick_speed': 1.5,
            'probe_distance': 2,
            'corner_inset': 3,
        },
        'patrol': {
            'crawl_time': [90, 150],
            'wait_time': [20, 40],
        },
        'states': {
            'crawl': {},
            'wait': {},
            'hurt': {
                'next_state': 'crawl',
            },
            'death': {},
            'dead': {},
        }
    }
}
