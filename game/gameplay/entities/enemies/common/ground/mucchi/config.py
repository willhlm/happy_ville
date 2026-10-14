"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    'mucchi': {
        'health': 3,
        'initial_state': 'idle',
        # Directional attack zone: [distance away from the surface, half-width].
        'distances': {'attack': [96, 48]},
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
                    'directional_attack': {
                        'next_state': 'attack_pre',
                        'distance': 'attack',
                        'score': 100,
                        'priority': 1,
                        'cooldown': 'attack',
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
