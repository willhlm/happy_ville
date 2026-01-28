WOLFIES_CONFIG = {
    'health': 2,
    'attack_distance': [100, 50],
    'jump_distance': [240, 50],
    'ability': 'dash',

    'patterns': {
        "slash": {
            "weight": 4,
            "range": "close",
            "tasks": [
                {"task": "attack1_pre"},
                {"task": "attack1_main"},
                {"task": "attack1_post"},
                {"task": "wait", "duration": 20},
                {"task": "think"},
            ]
        },

        "combo_slash": {
            "weight": 4,
            "range": "close",
            "tasks": [
                {"task": "attack1_pre"},
                {"task": "attack1_main"},
                {"task": "attack2_pre"},
                {"task": "attack2_main"},
                {"task": "attack2_post"},
                {"task": "wait", "duration": 40},
                {"task": "think"},
            ]
        },
        "jump_and_slam": {
            "weight": 3,
            "range": "mid",
            "tasks": [
                {"task": "jump_pre"},
                {"task": "jump_main"},
                {"task": "fall_pre"},
                {"task": "fall_main"},
                {"task": "slam_pre"},
                {"task": "slam_main"},
                {"task": "slam_post"},
                {"task": "wait", "duration": 80},
                {"task": "think"}
            ]
        },
        "run_attack": {
            "weight": 2,
            "range": "far",
            "tasks": [
                {"task": "run_pre", "speed_multiplier": 0.5},  # Shorter wind-up
                {"task": "run_main", "speed_multiplier": 1.4},  # Keep running even if close
                {"task": "run_attack_pre"},
                {"task": "run_attack_main"},
                {"task": "run_attack_post"},
                {"task": "wait", "duration": 30},
                {"task": "think"}
            ]
        },
        "retreat_then_jump": {
            "weight": 1,
            "range": "any",  # Flexible
            "tasks": [
                {"task": "wait", "duration": 15},
                {"task": "turn_around"},
                {"task": "wait", "duration": 15},
                {"task": "jump_pre"},
                {"task": "jump_main"},
                {"task": "fall_pre"},
                {"task": "fall_main"},
                {"task": "land"},            
                {"task": "think"}
            ]
        }
    }
}
