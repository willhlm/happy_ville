from ...room_config import RoomConfig

DEFAULT_ROOM_CONFIG = RoomConfig(
    weather={
        "wind": {
            "layers": {
                "bg1": {"velocity": [-2, 0.1], "duration_range": [3000, 7000]},
                "bg2": {"velocity": [-2, 0.1], "duration_range": [3000, 7000]},
                "bg3": {"velocity": [-2, 0.1], "duration_range": [3000, 7000]},
            }
        },
        "rain": {
            "layers": {
                "bg1": {"number_particles": 20},
            }
        },
        "fog": {
            "layers": {
                "bg1": {"intensity": 0.5, "colour": (0, 0, 0, 1)},
                "bg2": {"intensity": 1.0, "colour": (0, 0, 0, 1)},
                "bg3": {"intensity": 0.3, "colour": (0, 0, 0, 1)},
                "bg4": {"intensity": 0.5, "colour": (0, 0, 0, 1)},
                "bg5": {"intensity": 1.0, "colour": (0, 0, 0, 1)},
            }
        },
    }
)

ROOM_CONFIGS = {
    "2": RoomConfig(ambient_light=(30 / 255, 30 / 255, 30 / 255, 230 / 255)),
}
