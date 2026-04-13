import math

import pygame

from engine import constants as C

from gameplay.entities.items import SoulEssence
from gameplay.entities.areas import *
from gameplay.entities.visuals.particles import screen_particles
from gameplay.world.camera.stop import Stop

from gameplay.entities.interactables import *
from gameplay.entities.platforms import *
from gameplay.entities.visuals.environments import *

from ..helpers import calculate_object_position, props_list_to_dict, resolve_tileset
from ..map_data import LoadContext, MapDefinition


class SpawnerCommon:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.tile_size = C.tile_size
        self.viewport_center = self.game_objects.game.viewport_center


def shape_object_position(obj, parallax, offset, viewport_center):
    new_map_diff = [-viewport_center[0], -viewport_center[1]]
    return [
        int(obj["x"]) - math.ceil((1 - parallax[0]) * new_map_diff[0]) + offset[0],
        int(obj["y"]) - math.ceil((1 - parallax[1]) * new_map_diff[1]) + offset[1],
    ]
