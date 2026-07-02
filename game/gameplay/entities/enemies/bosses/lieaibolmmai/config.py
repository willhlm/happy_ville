CONFIG = {
    "health": 4,
    "attack_distance": [80, 120],
    "jump_distance": [220, 150],
    "walk_speed": 1.4,
    "walk_duration": 50,
    "selector": {
        "mode": "random",
    },
    "cooldowns": {
        "melee_attack": [50, 80],
        "slam_attack": [50, 80],
        "roll_attack": [200, 250],
    },
    "hurt_recovery": 220,
    "initial_state": "idle",
    "encounter_intro_tasks": [
        {"task": "roar_pre"},
        {"task": "roar_main"},
        {"task": "roar_post"},
        {"task": "think"},
    ],
    "patterns": {
        "attack": {
            "weight": 5,
            "range": "close",
            "cooldown": "melee_attack",
            "tasks": [
                {"task": "attack_pre"},
                {"task": "attack_main"},
                {"task": "attack_post"},
                {"task": "wait", "duration": 12},
                {"task": "think"},
            ],
        },
        "slam": {
            "weight": 4,
            "range": "mid",
            "cooldown": "slam_attack",
            "tasks": [
                {"task": "slam_pre"},
                {"task": "slam_main"},
                {"task": "slam_post"},
                {"task": "wait", "duration": 14},
                {"task": "think"},
            ],
        },
        "roll": {
            "weight": 2,
            "range": "far",
            "cooldown": "roll_attack",
            "tasks": [
                {"task": "roll_attack_pre"},
                {"task": "roll_attack_main"},
                {"task": "roll_attack_post"},
                {"task": "wait", "duration": 18},
                {"task": "think"},
            ],
        },
        "walk": {
            "weight": 2,
            "range": "any",
            "tasks": [
                {"task": "walk", "duration": 50},
                {"task": "think"},
            ],
        },
    },
}
