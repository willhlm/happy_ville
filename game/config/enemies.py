"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIGS = {
    'rav': {
        'health': 4,
        'speeds': {
            'chase': 1,
            'patrol': 0.3
        },
        'distances': {
            'aggro': [200, 20],
            'attack': [50, 150],
            'jump': [100, 150]
        },
        'cooldowns': {
            'melee_attack': [50, 80],#min max
            'jump_attack': [50, 150]#min max
        },
        'timers': {
            'patrol': [80, 220],#min max
            'hurt_recovery': 250
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
            'melee_attack': [50, 80],#min max
            'jump_attack': [50, 150]#min max
        },
        'timers': {
            'patrol': [80, 220],#min max
            'hurt_recovery': 150
        }
    }
}