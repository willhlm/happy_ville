from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class MusicTrackConfig:
    folder: str
    key: str
    index: int
    volume: float
    loop: int = -1
    fade: int = 1000


@dataclass
class RoomConfig:
    music: Optional[List[MusicTrackConfig]] = None
    weather: Optional[Dict[str, Any]] = None
    live_blur: Optional[bool] = None
    ambient_light: Optional[Any] = None
    player_lights: Optional[List[Dict[str, Any]]] = None


def merge_room_configs(*configs: RoomConfig) -> RoomConfig:
    merged = RoomConfig()
    for config in configs:
        if config is None:
            continue
        if config.music is not None:
            merged.music = deepcopy(config.music)
        if config.weather is not None:
            merged.weather = deepcopy(config.weather)
        if config.live_blur is not None:
            merged.live_blur = config.live_blur
        if config.ambient_light is not None:
            merged.ambient_light = deepcopy(config.ambient_light)
        if config.player_lights is not None:
            merged.player_lights = deepcopy(config.player_lights)
    return merged


def music_track(folder: str, key: str, index: int, volume: float, loop: int = -1, fade: int = 1000):
    return MusicTrackConfig(folder=folder, key=key, index=index, volume=volume, loop=loop, fade=fade)
