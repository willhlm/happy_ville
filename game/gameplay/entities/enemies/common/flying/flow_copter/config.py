ENEMY_CONFIG = {
    'flow_copter': {
        'health': 2,
        'initial_state': 'accend',
        'speeds': {
            'horizontal': 0.18,
            'accend': 2.4,
            'deccend': 0.6,
        },
        'movement': {
            'accend_time': 50,
            'deccend_time': 200,
            'horizontal_range': 40,
        },
        'light': {
            'radius': 90,
            'min_radius': 24,
            'colour': [255, 245, 200],
            'alpha': 230,
            'fade_floor': 30,
        },
        'timers': {'hurt_recovery': [150, 200]},
        
        'states': {
            'wait': {},
            'death': {},
            'dead': {},
            'accend': {},
            'deccend': {},
        }
    }
}
