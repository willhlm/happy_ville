from ...room_config import RoomConfig, music_track

DEFAULT_ROOM_CONFIG = RoomConfig(
    music=[music_track("assets/audio/music/maps/hlifblom/", "music", 1, 0.1)],
    particles={
        "layers": {
            "bg2": {"particle": "Circles", "number_particles": 20},
            "bg3": {"particle": "Circles", "number_particles": 20},
            "bg4": {"particle": "Circles", "number_particles": 20},
            "bg5": {"particle": "Circles", "number_particles": 20},
            "bg6": {"particle": "Circles", "number_particles": 20},
            "bg7": {"particle": "Circles", "number_particles": 20},
            "bg8": {"particle": "Circles", "number_particles": 20},
            "bg9": {"particle": "Circles", "number_particles": 20},
        }
    },
    ambient_light=(30 / 255, 30 / 255, 30 / 255, 230 / 255),
    player_lights=[{"colour": [255, 255, 255, 255], "normal_interact": False}],
)

ROOM_CONFIGS = {}
