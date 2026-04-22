from ...room_config import RoomConfig, music_track

DEFAULT_ROOM_CONFIG = RoomConfig(
    music=[music_track("assets/audio/music/maps/crystal_mines", "ambient", 1, 0.2)],
    ambient_light=(50 / 255, 50 / 255, 100 / 255, 170 / 255),
    player_lights=[{"colour": [255 / 255, 255 / 255, 255 / 255, 255 / 255], "normal_interact": False}],
)

ROOM_CONFIGS = {}
