from ...room_config import RoomConfig, music_track

DEFAULT_ROOM_CONFIG = RoomConfig(
    music=[music_track("assets/audio/music/maps/wake_up_forest/", "ambient", 1, 0.1)],
    ambient_light=[200 / 255, 200 / 255, 200 / 255, 255 / 255],
    player_lights=[{"colour": [200 / 255, 200 / 255, 200 / 255, 255 / 255], "normal_interact": False}],
)

ROOM_CONFIGS = {
    "99": RoomConfig(ambient_light=(30 / 255, 20030 / 255, 30 / 255, 230 / 255)),
}
