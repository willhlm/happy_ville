from gameplay.entities.interactables import DropletSource, Valve
from gameplay.entities.platforms import BridgePlatform, LiftCar, Piston
from gameplay.entities.platforms.dynamic.lift.controls import attach_controls

from ..helpers import calculate_object_position, props_list_to_dict, resolve_tileset
from .base import Biome
from .room_configs.golden_fields import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS
from gameplay.entities.visuals.environments import RotatingRig, WaterRelaySystem, Windmill


class Golden_fields(Biome):
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

            if id == 2:
                new_bridge = BridgePlatform(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_bridge)

            elif id == 3:
                if layer_name.startswith("fg"):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs

                new_drop = DropletSource(object_position, self.level.game_objects, parallax, layer_name, group)
                group.add(layer_name, new_drop)

            elif id == 4:
                kwargs = props_list_to_dict(properties)
                new_mill = Windmill(
                    object_position,
                    self.level.game_objects,
                    parallax,
                    layer_name,
                    kwargs.get("id"),
                )
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_mill)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_mill)

            elif id == 5:
                pass

            elif id == 6:
                self.level.game_objects.interactables.add(
                    Valve(object_position, self.level.game_objects, **props_list_to_dict(properties))
                )

            elif id == 7:
                self.level.game_objects.platforms.add(
                    Piston(object_position, self.level.game_objects, **props_list_to_dict(properties))
                )

            elif id == 8:
                rig = RotatingRig(
                    object_position,
                    self.level.game_objects,
                    parallax,
                    layer_name,
                    **props_list_to_dict(properties),
                )
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, rig)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, rig)

            elif id == 9:
                props = props_list_to_dict(properties)
                path_ref = props.get("path")
                path_data = ctx.references.get("paths_by_id", {}).get(int(path_ref)) if path_ref else None
                if path_data is None:
                    raise ValueError(f"Lift {props.get('signal_id', props.get('id', ''))!r} references unknown path {path_ref!r}")
                props["path_points"] = path_data["points"]
                sprite_path = "assets/sprites/entities/platforms/lifts/liftcar/body/"
                lift = LiftCar(object_position, self.level.game_objects, sprite_path, **props)
                self.level.game_objects.platforms.add(lift)
                attach_controls(lift, props)

            elif id == 10:
                props = props_list_to_dict(properties)
                path_ref = props.get("path")
                path_data = ctx.references.get("paths_by_id", {}).get(int(path_ref)) if path_ref else None
                if path_data is None:
                    raise ValueError(f"Lift {props.get('signal_id', props.get('id', ''))!r} references unknown path {path_ref!r}")
                props["path_points"] = path_data["points"]
                sprite_path = "assets/sprites/entities/platforms/lifts/lift/body/"
                lift = LiftCar(object_position, self.level.game_objects, sprite_path, **props)
                self.level.game_objects.platforms.add(lift)
                attach_controls(lift, props)                

            elif id == 11:
                #water relay system
                water = WaterRelaySystem(
                    object_position,
                    self.level.game_objects,
                    parallax,
                    layer_name,
                    **props_list_to_dict(properties),
                )
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, water)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, water)
