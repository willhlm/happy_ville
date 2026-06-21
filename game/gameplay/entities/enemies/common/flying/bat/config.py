ENEMY_CONFIG = {
    'bat': {
        'health': 1,
        'initial_state': 'hanging',
        'distances': {
            'aggro': [200, 140],
            'attack': [110, 110],
        },
        'behavior': {
            'alert_speed': 0.18,
            'alert_drop_distance': 24,
            'alert_stop_distance': 28,
        },
        'attack': {
            'crystal_drop_interval': [55, 80],
            'crystal_velocity': [0, 1.2],

            'spawn_offset': 96,
            'scream_shake_interval': 10,
            'scream_shake_amplitude': 2,
            'scream_shake_duration': 8,
            'scream_shake_scale': 0.96,

            'shockwave_size': [640, 640],
            'shockwave_reference_size': 140,
            'shockwave_alpha': 255,
            'shockwave_sine_scale': 20,
            'shockwave_alpha_decay':1,
            'shockwave_speed': 2.4,
            'shockwave_frequency':  4,
            'shockwave_width': 0.06,
            'shockwave_fade': 0.78,
            'shockwave_radial_fade_power': 1,
            'shockwave_noise_map_scale': [2.0, 2.0],
            'shockwave_noise_scale': 2.0,
            'shockwave_noise_strength': 0.02,
            'shockwave_colour': [255, 255, 255, 255],
        },
        'states': {
            'hanging': {},
            'drop': {},
            'alert': {},
            'attack_pre': {},
            'attack_main': {},
            'death': {},
            'dead': {},
        },
    }
}
