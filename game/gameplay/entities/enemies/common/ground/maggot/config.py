"""
Enemy configuration data.
All enemy stats defined here for easy balancing.
"""

ENEMY_CONFIG = {
    "maggot": {
        "health": 1,
        "initial_state": "fall",
        "speeds": {"run_away": 0.5},
        "distances": {"aggro": [200, 30]},
        "timers": {"hurt_recovery": [200, 250]},
        "states": {
            "fall": {},
            "land": {
                "next_state": "wait",
                "kwargs": {"time": 50, "next_state": "idle"},
            },
            "idle": {
                "deciders": {
                    "check_player": {
                        "next_state": "run_away",
                        "distance": "aggro",
                        "score": 100,
                        "priority": 1,
                    }
                }
            },
            "hurt": {
                "next_state": "wait",
                "kwargs": {"time": 50, "next_state": "idle"},
            },
            "run_away": {
                "deciders": {
                    "check_player_far": {
                        "next_state": "idle",
                        "distance": "aggro",
                        "score": 100,
                        "priority": 0,
                    },
                    "check_player_cross_over": {
                        "next_state": "wait",
                        "score": 80,
                        "priority": 1,
                        "kwargs": {"time": 100, "next_state": "run_away", "dir": -1},
                    },
                    "check_edge": {
                        "next_state": "wait",
                        "score": 90,
                        "priority": 2,
                        "kwargs": {"time": 60, "next_state": "run_away", "dir": -1},
                    },
                },
            },
        },
    }
}
