from engine.utils import functions

from gameplay.entities.interactables import DoorInteract
from gameplay.entities.platforms import BoulderPlatform, RightDoorPlatform
from gameplay.entities.visuals.environments import ThorMountain

from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.village import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Village(Biome):
    default_room_config = DEFAULT_ROOM_CONFIG
    room_configs = ROOM_CONFIGS

    def post_process(self, layer_name, parallax):
        if self.live_blur:
            if parallax[0] == 1:
                radius = 0.01
            else:
                radius = functions.blur_radius(parallax, max_blur=5)

            self.level.game_objects.game.screen_manager.append_shader("Blur_fast", [layer_name], radius=radius)
            if layer_name == "bg1":
                self.level.game_objects.game.screen_manager.append_shader("Blur_fast", ["player"], radius=radius)
                self.level.game_objects.game.screen_manager.append_shader("Blur_fast", ["player_fg"], radius=radius)

    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])

            source, firstgid, local_id = resolve_tileset(map_def, obj["gid"])
            if "objects" not in source:
                continue
            id = local_id

            if id == 0:
                thor_mtn = ThorMountain(object_position, self.level.game_objects, parallax, layer_name, self.live_blur)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, thor_mtn)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, thor_mtn)

            elif id == 2:
                kwarg = {}
                for property in properties:
                    if property["name"] == "ID":
                        kwarg["ID"] = property["value"]
                    elif property["name"] == "erect":
                        kwarg["erect"] = property["value"]
                    elif property["name"] == "key":
                        kwarg["key"] = property["value"]
                door = RightDoorPlatform(object_position, self.level.game_objects, **kwarg)
                door_i = DoorInteract(object_position, self.level.game_objects, door)
                self.level.game_objects.platforms.add(door)
                self.level.game_objects.interactables.add(door_i)

            elif id == 3:
                new_tree = BoulderPlatform(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_tree)
