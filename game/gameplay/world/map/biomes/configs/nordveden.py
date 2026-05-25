from ...room_config import RoomConfig, music_track

DEFAULT_ROOM_CONFIG = RoomConfig(
    music=[
        music_track("assets/audio/music/maps/nordveden/", "music", 1, 0.1),
        music_track("assets/audio/music/maps/nordveden/", "ambient", 2, 0.2),
    ],
    weather={
        "wind": {
            "layers": {
                "bg1": {"velocity": [-2, 0.1], "duration_range": [180, 420]},
                "bg2": {"velocity": [-2, 0.1], "duration_range": [180, 420]},
                "bg3": {"velocity": [-2, 0.1], "duration_range": [180, 420]},
            }
        },
        "rain": {
            "layers": {
                "bg1": {"number_particles": 20},
            }
        },
        "fog": {
            "layers": {
                "bg1": {"intensity": 0.5, "colour": (1, 1, 1, 1)},
                "bg2": {"intensity": 1.0, "colour": (1, 1, 1, 1)},
                "bg3": {"intensity": 0.3, "colour": (1, 1, 1, 1)},
                "bg4": {"intensity": 0.5, "colour": (1, 1, 1, 1)},
                "bg5": {"intensity": 1.0, "colour": (1, 1, 1, 1)},
            }
        },
    },
    particles={
        "layers": {
            "bg2": {"particle": "Vertical_circles", "number_particles": 20},
            "bg3": {"particle": "Vertical_circles", "number_particles": 20},
            "bg4": {"particle": "Vertical_circles", "number_particles": 20},
            "bg5": {"particle": "Vertical_circles", "number_particles": 20},
            "bg6": {"particle": "Vertical_circles", "number_particles": 20},
        }
    },
)

ROOM_CONFIGS = {
    room: RoomConfig(
        ambient_light=[100 / 255, 100 / 255, 100 / 255, 255 / 255],
        player_lights=[{"colour": [200, 200, 200, 200], "normal_interact": False}],
    )
    for room in ("11", "8", "7", "6", "5")
}
