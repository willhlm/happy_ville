PLANTIS_CONFIG = {
    "health": 10,
    "attack_distance": [0, 0],
    "jump_distance": [0, 0],
    "selector": {
        "mode": "random",
    },
    "hurt_recovery": 45,
    "patterns": {
        "idle": {
            "range": "any",
            "tasks": [
                {"task": "wait", "duration": 60},
                {"task": "think"},
            ],
        },
    },
    "encounter_intro_tasks": [
        {"task": "wait", "duration": 30},
        {"task": "roar"},
        {"task": "idle"},
    ],
}
