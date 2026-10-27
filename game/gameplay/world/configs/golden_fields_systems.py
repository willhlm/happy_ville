"""Authored Golden Fields puzzle data."""

# Controllers consume these definitions; they do not own them.
WATER_RELAY_ANGLES = (0, 90, 180, 270)

WINDMILL_NETWORKS = {
    "golden_fields_windmills": {
        "windmill_level": "golden_fields_2",
        "windmill_ids": ("windmill_1", "windmill_2", "windmill_3"),
        # These are world-state defaults, rather than map-load defaults.
        # Consumers can therefore be loaded before the windmill map is visited.
        "windmill_initial_states": {
            "windmill_1": "active",#idle#z
            "windmill_2": "active",#stuck
            "windmill_3": "active",#active
        },
    },
}

PISTON_PROFILES = {
    "golden_fields_default": {
        "off": {"visible_time": 30, "hidden_time": 180, "warning_time": 0},
        "on": {"mode": "always_visible"},
    },
}

ROTATING_RIG_PROFILES = {
    "golden_fields_default": {
        # Rotation speed uses the rig's existing degrees per game-time unit.
        "off": {"rotation_speed": 0.0},
        "on": {"rotation_speed": 1.0},
    },
}

WATER_RELAYS = {
    "water_relay_1": {
        "state_level": "golden_fields_27",
        "power_source": "golden_fields_windmills",
        "initial_angle": 0,
    },
}


def piston_profile(profile_id, powered):
    """Return the authored piston behavior for a binary power state."""
    try:
        profiles = PISTON_PROFILES[profile_id]
    except KeyError as error:
        raise KeyError(f"Unknown Golden Fields piston profile '{profile_id}'.") from error
    return profiles["on" if powered else "off"]


def rotating_rig_profile(profile_id, powered):
    """Return the authored rig behavior for a binary power state."""
    try:
        profiles = ROTATING_RIG_PROFILES[profile_id]
    except KeyError as error:
        raise KeyError(
            f"Unknown Golden Fields rotating rig profile '{profile_id}'."
        ) from error
    return profiles["on" if powered else "off"]
