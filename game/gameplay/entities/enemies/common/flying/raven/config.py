ENEMY_CONFIG = {
    'raven': {
        'health': 1,
        'initial_state': 'patrol',
        'speeds': {
            'fall': 0.45,
            'fall_max': 1.15,
            'ground_snap': 0.35,
            'takeoff': 0.42,
            'hover': 0.28,
            'dive': 7.4,
        },
        'distances': {
            'aggro': [220, 150],
            'attack': [120, 150],
        },
        'hover': {
            'height': 72,
            'side_offset': 28,
            'align_padding': 18,
            'attack_delay': 36,
            'give_up_time': 90,
        },
        'attack': {
            'pre_time': 22,
            'duration': 40,
            'recover_time': 24,
        },

        'timers': {'hurt_recovery': [150, 200]},
        'cooldowns': {'melee_attack': [110, 160]},
        'states': {
            'patrol': {
                'deciders': {
                    'check_player': {
                        'next_state': 'chase',
                        'score': 1,
                        'priority': 1,
                    },
                },
            },
            'chase': {
                'deciders': {
                    'chase_give_up': {
                        'next_state': 'patrol',
                        'score': 1,
                        'priority': 1,
                        'give_up_time': 90,
                    },
                },
            },
            'attack_pre': {},
            'attack_main': {},
            'attack_post': {},
            'hurt': {
                'next_state': 'patrol',
            },
        },
    },
}
