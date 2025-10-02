"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIGS = {
    'rav': {
        'health': 4,
        'speeds': {'chase': 1, 'patrol': 0.3},
        'distances': {'aggro': [200, 20], 'attack': [50, 150], 'jump': [100, -10]},
        'cooldowns': {
            'melee_attack': [50, 80],
            'jump_attack': [50, 80]
        },
        'timers': {'patrol': [80, 220], 'hurt_recovery': 250},
        'decisions': {
            'jump_attack': {'score': 80, 'priority': 1, 'cooldown': 'jump_attack'},
            'melee_attack': {'score': 40, 'priority': 1, 'cooldown': 'melee_attack'},
            'wait_to_chase': {'score': 80, 'priority': 1},
            'patrol_end_wait': {'score':50,'priority':0,'time_range':[80,220]},
            'edge_wait': {'score':90, 'priority':2, 'time':60, 'next_state':'patrol', 'dir':-1},
            'chase_giveup': {'score':50,'priority':1,'time':400,'next_state':'patrol'},
        }
    }
}