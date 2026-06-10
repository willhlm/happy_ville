ENEMY_CONFIG = {
    'crystal_fly': {
        'health': 3,
        'initial_state': 'patrol',
        'speeds': {
            'patrol': 0.12,
            'chase': 0.7,
        },
        'distances': {
            'aggro': [200, 140],
            'attack': [110, 110],
        },
        'behavior': {
            'patrol_radius': [36, 64],
            'patrol_angle_range': [0, 180],
            'patrol_angle_offset': [-24, 24],
            'patrol_vertical_bias': 8,
            'sway_cap': 0.3,
            'sway_factor': 0.9,
            'sway_speed': 5,
        },
        'timers': {
            'hurt_recovery': [150, 200],
        },
        'cooldowns': {
            'melee_attack': [110, 160],
        },
        'states': {
            'patrol': {
                'deciders': {
                    'patrol_position_end': {
                        'next_state': 'wait',
                        'score': 80,
                        'priority': 1,
                        'kwargs': {'time': 20, 'next_state': 'patrol'},
                    },
                    'check_collisions': {
                        'next_state': 'wait',
                        'directions': ['left', 'right', 'top', 'bottom'],
                        'score': 80,
                        'priority': 1,
                        'kwargs': {'time': 20, 'next_state': 'patrol'},
                    },
                    'check_player': {
                        'next_state': 'wait',
                        'score': 90,
                        'priority': 2,
                        'kwargs': {'time': 10, 'next_state': 'chase'},
                    },
                },
            },
            'chase': {
                'deciders': {
                    'melee_attack': {
                        'next_state': 'attack_pre',
                        'score': 90,
                        'priority': 2,
                        'cooldown': 'melee_attack',
                    },
                    'chase_give_up': {
                        'next_state': 'wait',
                        'score': 50,
                        'priority': 1,
                        'give_up_time': 220,
                        'kwargs': {'time': 30, 'next_state': 'patrol'},
                    },
                },
            },
            'attack_pre': {},
            'attack_main': {
                'kwargs': {
                    'next_state': 'chase',
                },
            },
            'hurt': {
                'next_state': 'patrol',
            },
            'wait': {},
            'death': {},
            'dead': {},
        },
    }
}
