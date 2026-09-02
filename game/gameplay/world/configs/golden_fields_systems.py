"""Authored Golden Fields puzzle data."""

# Controllers consume these definitions; they do not own them.
WINDMILL_NETWORKS = {
    "golden_fields_liquid": {
        "windmill_level": "golden_fields_2",
        "windmill_ids": ("windmill_1", "windmill_2", "windmill_3"),
        # These are world-state defaults, rather than map-load defaults.
        # Consumers can therefore be loaded before the windmill map is visited.
        "windmill_initial_states": {
            "windmill_1": "stuck",
            "windmill_2": "idle",
            "windmill_3": "active",
        },
    },
}

PISTON_PROFILES = {
    "golden_fields_default": {
        0: {"visible_time": 30, "hidden_time": 180, "warning_time": 0},
        1: {"visible_time": 30, "hidden_time": 180, "warning_time": 0},
        2: {"visible_time": 75, "hidden_time": 90, "warning_time": 0},
        "all": {"mode": "always_visible"},
    },
}
