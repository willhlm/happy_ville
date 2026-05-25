from gameplay.entities.interactables import BubbleSource, DropletSource, FallingRockSource, InteractableCaveGrass, Spikes, Bloomer
from gameplay.entities.platforms import Bubble, FlowerPlatform
from gameplay.entities.visuals.environments import BackgroundCaveGrass, LjusMaskar, Vines_2

from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.hlifblom import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Hlifblom(Biome):
    default_room_config = DEFAULT_ROOM_CONFIG
    room_configs = ROOM_CONFIGS

    def post_process(self, layer_name, parallax):
        pass
        
    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])
            source, firstgid, local_id = resolve_tileset(map_def, obj["gid"])
            if "objects" not in source:
                continue
            id = local_id

            if id == 0:
                if parallax == [1, 1]:
                    new_grass = InteractableCaveGrass(object_position, self.level.game_objects)
                    self.level.game_objects.interactables.add(new_grass)
                else:
                    new_grass = BackgroundCaveGrass(object_position, self.level.game_objects, parallax, layer_name)
                    if layer_name.startswith("fg"):
                        self.level.game_objects.all_fgs.add(layer_name, new_grass)
                    else:
                        self.level.game_objects.all_bgs.add(layer_name, new_grass)

            elif id == 1:
                new_grass = LjusMaskar(object_position, self.level.game_objects, parallax, layer_name)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_grass)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_grass)

            elif id == 2:
                if layer_name.startswith("fg"):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs

                new_drop = DropletSource(object_position, self.level.game_objects, parallax, layer_name, group)
                group.add(layer_name, new_drop)

            elif id == 3:
                new_rock = FallingRockSource(object_position, self.level.game_objects, parallax, layer_name)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_rock)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_rock)

            elif id == 4:
                new_vine = Vines_2(object_position, self.level.game_objects, parallax, layer_name)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_vine)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_vine)

            elif id == 5:
                prop = {}
                for property in properties:
                    if property["name"] == "lifetime":
                        prop["lifetime"] = property["value"]
                    elif property["name"] == "init_delay":
                        prop["init_delay"] = property["value"]
                    elif property["name"] == "spawnrate":
                        prop["spawnrate"] = property["value"]
                    elif property["name"] == "cos_amp_scaler":
                        prop["cos_amp_scaler"] = property["value"]
                    elif property["name"] == "state":
                        state = property["value"]

                bubble_source = BubbleSource(object_position, self.level.game_objects, **prop)
                self.level.game_objects.interactables.add(bubble_source)

            elif id == 6:
                spikes = Spikes(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(spikes)

            elif id == 7:
                prop = {}
                for property in properties:
                    if property["name"] == "lifetime":
                        prop["lifetime"] = property["value"]

                new_bubble = Bubble(object_position, self.level.game_objects, **prop)
                self.level.game_objects.platforms.add(new_bubble)

            elif id == 8:
                new = Bloomer(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(new)

            elif id == 9:#flower platform
                new_flower = FlowerPlatform(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_flower)