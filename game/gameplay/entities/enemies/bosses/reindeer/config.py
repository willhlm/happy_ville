REINDEER_CONFIG = {
    "health": 2,
    "attack_distance": [100, 50],
    "jump_distance": [240, 50],
    "selector": {
        "mode": "random",
    },
    "patterns": {
        "combo_slash": {
            "weight": 4,
            "range": "close",
            "tasks": [
                {"task": "attack_pre"},
                {"task": "attack_main"},
                {"task": "wait", "duration": 20},
                {"task": "think"},
            ],
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
                {"task": "think"},
            ],
        },
        "charge_combo": {
            "weight": 2,
            "range": "far",
            "tasks": [
                {"task": "charge_pre"},
                {"task": "charge_main"},
                {"task": "charge_run"},
                {"task": "charge_attack_pre"},
                {"task": "charge_attack"},
                {"task": "charge_post"},
                {"task": "wait", "duration": 30},
                {"task": "think"},
            ],
        },
        "retreat_then_jump": {
            "weight": 1,
            "range": "any",
            "tasks": [
                {"task": "wait", "duration": 15},
                {"task": "turn_around"},
                {"task": "wait", "duration": 15},
                {"task": "jump_pre"},
                {"task": "jump_main"},
                {"task": "fall_pre"},
                {"task": "fall_main"},
                {"task": "think"},
            ],
        },
    },
}
