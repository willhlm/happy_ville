"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIGS = {
    'rav': {
        'health': 3,
        'speeds': {
            'chase': 0.8,
            'patrol': 0.3
        },
        'distances': {
            'aggro': [200, 20],
            'attack': [50, 150],
            'jump': [100, 150]
        },
        'cooldowns': {
            'melee_attack': 120,
            'jump_attack': 200
        },
        'timers': {
            'patrol': 220,
            'hurt_recovery': 200
        }
    },
    
    'rav_elite': {
        'health': 6,
        'speeds': {
            'chase': 1.2,
            'patrol': 0.5
        },
        'distances': {
            'aggro': [250, 30],
            'attack': [60, 150],
            'jump': [120, 150]
        },
        'cooldowns': {
            'melee_attack': 80,   # Faster attacks
            'jump_attack': 150
        },
        'timers': {
            'patrol': 180,
            'hurt_recovery': 150
        }
    }
}