"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'mucchi': {
        'health': 3,
        'initial_state': 'idle',
        'distances': {
            'ready': [320, 160],
            'attack': [96, 48],
        },
        'hurtbox': {'reach': 64, 'width': 32},
        'cooldowns': {
            'attack': [50, 80],
        },
        'timers': {
            'hurt_recovery': [200, 250],
            'hurt_stun': 10,
        },

        'states': {
            'idle': {
                'deciders': {
                    'directional_ready': {
                        'next_state': 'ready',
                        'distance': 'ready',
                        'score': 100,
                        'priority': 1,
                    },
                },
            },
            'ready': {
                'deciders': {
                    'directional_attack': {
                        'next_state': 'attack_pre',
                        'distance': 'attack',
                        'score': 100,
                        'priority': 1,
                        'cooldown': 'attack',
                    },
                    'directional_idle': {
                        'next_state': 'idle',
                        'distance': 'ready',
                        'condition': 'outside',
                        'score': 100,
                        'priority': 1,
                    },
                },
            },
            'hurt': {'next_state': 'idle'},
            'death': {},
            'dead': {},
            'attack_pre': {},
            'attack_main': {},
            'attack_post': {},
        }
    }
}
