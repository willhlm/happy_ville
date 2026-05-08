from ...room_config import RoomConfig, music_track

DEFAULT_ROOM_CONFIG = RoomConfig(
    music=[music_track("assets/audio/music/maps/hlifblom/", "music", 1, 0.1)],
    ambient_light=(30 / 255, 30 / 255, 30 / 255, 255 / 255),
    player_lights=[{"colour": [255 / 255, 255 / 255, 255 / 255, 255 / 255], "normal_interact": False}],
)

ROOM_CONFIGS = {}
