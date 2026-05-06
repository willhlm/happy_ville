ENEMY_CONFIG = {
    'moth': {
        'health': 3,
        'initial_state': 'patrol',
        'speeds': {
            'patrol': 0.12,
            'chase': 0.5,
        },
        'distances': {
            'aggro': [260, 180],
        },
        'stimulus': {
            'bounds': [320, 220],
            'channel_weights': {
                'light': 0.0,
            },
            'tag_weights': {
                'flower': 0.65,
                'player': 0.1,
            },
        },
        'behavior': {
            'patrol_radius': [36, 84],
            'patrol_angle_range': [0, 180],
            'patrol_angle_offset': [-24, 24],
            'patrol_vertical_bias': 10,
            'sway_cap': 0.26,
            'sway_factor': 1.15,
            'sway_speed': 5,
            'give_up_time': 120,
            'wait_time': [18, 36],
        },
        'timers': {
            'hurt_recovery': [150, 200],
        },
        'states': {
            'patrol': {
                'deciders': {
                    'check_attraction_target': {
                        'next_state': 'chase',
                        'score': 100,
                        'priority': 2,
                    },
                    'patrol_position_end': {
                        'next_state': 'wait',
                        'score': 80,
                        'priority': 1,
                        'kwargs': {
                            'time': 28,
                            'next_state': 'patrol',
                        },
                    },
                    'check_collisions': {
                        'next_state': 'wait',
                        'directions': ['left', 'right', 'top', 'bottom'],
                        'score': 80,
                        'priority': 1,
                        'kwargs': {
                            'time': 20,
                            'next_state': 'patrol',
                        },
                    },
                },
            },
            'chase': {
                'kwargs': {
                    'stop_distance': 18,
                },
                'deciders': {
                    'attraction_target_give_up': {
                        'next_state': 'wait',
                        'score': 80,
                        'priority': 1,
                        'give_up_time': 120,
                        'kwargs': {
                            'time': 24,
                            'next_state': 'patrol',
                        },
                    },
                },
            },
            'wait': {
                'deciders': {
                    'check_attraction_target': {
                        'next_state': 'chase',
                        'score': 100,
                        'priority': 2,
                    },
                },
            },
        },
    }
}
