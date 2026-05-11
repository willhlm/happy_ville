from ...room_config import RoomConfig

DEFAULT_ROOM_CONFIG = RoomConfig(
    weather={
        "rain": {
            "layers": {
                "bg1": {"number_particles": 20},
            }
        },
        "fog": {
            "layers": {
                "bg1": {"intensity": 0.5, "colour": (1, 1, 1, 1)},
                "bg2": {"intensity": 1.0, "colour": (1, 1, 1, 1)},
                "bg3": {"intensity": 0.3, "colour": (0, 0, 0, 1)},
                "bg4": {"intensity": 0.5, "colour": (0, 0, 0, 1)},
                "bg5": {"intensity": 1.0, "colour": (0, 0, 0, 1)},
                "bg6": {"intensity": 1.0, "colour": (0, 0, 0, 1)},
                "bg7": {"intensity": 1.0, "colour": (0, 0, 0, 1)},
            }
        },
    },
    ambient_light=[30 / 255, 30 / 255, 30 / 255, 170 / 255],
    player_lights=[
        {
            "colour": [255, 255, 255, 255],
            "shadow_interact": True,
            "platform_interact": True,
            "normal_interact": False,
        }
    ],
)

ROOM_CONFIGS = {}
