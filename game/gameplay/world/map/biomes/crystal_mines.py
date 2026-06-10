from gameplay.entities.areas import Hole
from gameplay.entities.interactables import CrystalSource
from gameplay.entities.platforms import ConveyorBelt, Smacker
from gameplay.entities.visuals.environments import Crystals

from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.crystal_mines import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Crystal_mines(Biome):
    default_room_config = DEFAULT_ROOM_CONFIG
    room_configs = ROOM_CONFIGS

    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])
            source, firstgid, local_id = resolve_tileset(map_def, obj["gid"])
            if "objects" not in source:
                continue
            id = local_id

            if id == 7:
                kwarg = {}
                for property in properties:
                    if property["name"] == "right":
                        kwarg["right"] = property["value"]
                    elif property["name"] == "up":
                        kwarg["up"] = property["value"]
                    elif property["name"] == "vertical":
                        kwarg["vertical"] = property["value"]

                new_conveyor_belt = ConveyorBelt(object_position, self.level.game_objects, object_size, **kwarg)
                self.level.game_objects.platforms.add(new_conveyor_belt)

            elif id == 8:
                kwarg = {"hole": Hole(object_position, self.level.game_objects, object_size)}
                for property in properties:
                    if property["name"] == "distance":
                        kwarg["distance"] = property["value"]

                new_smacker = Smacker(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.platforms.add(new_smacker)

            elif id == 10:
                kwarg = {}
                for property in properties:
                    if property["name"] == "dir":
                        pos = property["value"]
                        string_list = pos.split(",")
                        kwarg["dir"] = [int(item) for item in string_list]
                    elif property["name"] == "velocity":
                        amp = property["value"]
                        string_list = amp.split(",")
                        kwarg["amp"] = [int(item) for item in string_list]
                    elif property["name"] == "lifetime":
                        kwarg["lifetime"] = int(property["value"])
                    elif property["name"] == "frequency":
                        kwarg["frequency"] = int(property["value"])
                
                new_emitter = CrystalSource(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_emitter)

            elif id == 11:
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, layer_name, "crystal_1")
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_crystal)

            elif id == 12:
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, layer_name, "crystal_2")
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_crystal)

            elif id == 13:
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, layer_name, "crystal_3")
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_crystal)

            elif id == 14:
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, layer_name, "crystal_4")
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_crystal)

            elif id == 15:
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, layer_name, "crystal_5")
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_crystal)
