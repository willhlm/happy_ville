import pygame
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

@dataclass
class MapDefinition:
    """
    Parsed Tiled map data (unchanged schema), but wrapped for clarity.
    """
    biome_room_name: str
    biome_name: str
    map_data: dict
    statics_firstgid: int
    interactables_firstgid: int
    objects_firstgid: int
    platforms_firstgid: int
    tileset_ranges: list

    @property
    def room_id(self):
        return self.biome_room_name[self.biome_room_name.rfind("_") + 1 :]

@dataclass
class LoadContext:
    """
    Per-load transient state: anything that should NOT live forever on MapLoader.
    """
    biome_room_name: str
    spawn: Any

    references: Dict[str, list] = field(default_factory=lambda: {"bg_fade": []})
    spawned: bool = False

    # caches for this load
    spritesheet_dict: Dict[int, pygame.Surface] = field(default_factory=dict)
