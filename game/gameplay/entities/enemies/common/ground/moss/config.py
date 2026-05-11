"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    "moss": {
        "health": 3,
        "speeds": {"patrol": 0.5},
        "distances": {"attack": [150, 30]},
        "cooldowns": {"melee_attack": [200, 300]},
        "timers": {"hurt_recovery": [200, 250]},
        "states": {
            "idle": {},
            "hurt": {},
            'patrol': {
                'deciders':{
                    'melee_attack': {'next_state':'attack_pre', 'distance': 'attack', 'score': 70, 'priority': 1, 'cooldown': 'melee_attack'}, 
                    'patrol_end': {'next_state':'wait', 'score':50, 'priority':0, 'patrol_time': [150, 200], 'kwargs': {'next_state': 'patrol', 'time':50}}, 
                    'check_edge': {'next_state':'wait', 'score':90, 'priority':2, 'kwargs': {'time':60, 'next_state':'patrol', 'dir':-1}}
                    },
            },
        },
    }
}
