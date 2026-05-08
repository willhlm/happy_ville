ENEMY_CONFIG = {
    'larv': {
        'health': 3,
        'initial_state': 'patrol',
        'speeds': {
            'crawl': 0.5,
            'ground_snap': 0.2,
        },
        'timers': {
            'hurt_recovery': [200, 250],
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
            'hanging': {},
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

    'larv_poison': {
        'health': 3,
        'initial_state': 'chase',
        'speeds': {
            'crawl': 0.4,
            'ground_snap': 0.2,
        },
        'timers': {
            'hurt_recovery': [200, 250],
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
            'surface_edge_lookahead': 8,
        },
        'states': {
            'chase': {
                'deciders': {
                    'surface_edge': {
                        'next_state': 'wait',
                        'score': 90,
                        'priority': 2,
                        'reasons': ['unsupported_surface'],
                        'lookahead': 8,
                        'kwargs': {'time': 35, 'next_state': 'chase', 'turn': True},
                    },
                },
            },
            'hanging': {},
            'fall': {},
            'land': {
                'kwargs': {
                    'next_state': 'wait',
                    'next_state_kwargs': {'next_state': 'chase', 'time': 150},
                },
            },
            'wait': {},
            'hurt': {
                'next_state': 'chase',
            },
            'attack_pre': {},
            'attack_main': {},
        }
    },
    
    'larv_jr': {
        'health': 3,
        'initial_state': 'patrol',
        'speeds': {
            'crawl': 0.5,
            'ground_snap': 0.2,
        },
        'timers': {
            'hurt_recovery': [200, 250],
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
            'hanging': {},
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
