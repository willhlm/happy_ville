"""
Enemy configuration data.
"""

ENEMY_CONFIG = {
    'base': {
        'health': 4,
        'speeds': {'chase': 1.0, 'patrol': 0.55, 'charge': 2.0},
        'distances': {'aggro': [250, 25], 'attack': [200, 25], 'charge_commit': [80, 25]},
        'cooldowns': {
            'melee_attack': [90, 130],
        },
        'timers': {
            'hurt_recovery': [160, 210],
        },
        'states': {
            'patrol': {
                'deciders': {
                    'check_player': {'next_state': 'wait', 'score': 80, 'priority': 1, 'kwargs': {'time': 10, 'next_state': 'chase'}},
                    'patrol_end': {'next_state': 'wait', 'score': 50, 'priority': 0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time': 50}},
                    'check_edge': {'next_state': 'wait', 'score': 90, 'priority': 2, 'kwargs': {'time': 60, 'next_state': 'patrol', 'dir': -1}},
                },
            },
            'chase': {
                'deciders': {
                    'melee_attack': {'next_state': 'attack_pre', 'score': 80, 'priority': 1, 'cooldown': 'melee_attack'},
                    'chase_give_up': {'next_state': 'wait', 'score': 50, 'priority': 1, 'give_up_time': 400, 'kwargs': {'next_state': 'patrol', 'time': 30}},
                    'check_edge': {'next_state': 'wait', 'score': 90, 'priority': 2, 'kwargs': {'time': 60, 'next_state': 'patrol', 'dir': -1}},
                },
            },
            'hurt': {
                'next_state': 'chase',
            },
        },
    }
}
