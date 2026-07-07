from .common import ComponentPlatform, SpawnerCommon, calculate_object_position, props_list_to_dict, shape_object_position


class PlatformSpawner(SpawnerCommon):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.platform_defaults = {
            "solid": True,
            "oneway_up": False,
            "damage": False,
            "damage_on_land": False,
            "move": False,
            "disappear_on_stand": False,
            "breakable": False,
        }

    def _bool(self, value, default=False):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        return str(value).strip().lower() in ("1", "true", "yes", "y", "on")

    def _components_from_flags(self, props: dict) -> list:
        components = []

        if self._bool(props.get("damage_on_land")):
            components.append("damage_on_land")
        elif self._bool(props.get("damage")):
            components.append("damage")
        elif self._bool(props.get("oneway_up")):
            components.append("oneway_up")
        elif self._bool(props.get("solid"), default=True):
            components.append("solid")

        if self._bool(props.get("move")) or props.get("path_points"):
            components.append("move")
            components.append("carry_on_top")
        if self._bool(props.get("float_on_liquid")):
            components.append("float_on_liquid")
            if "carry_on_top" not in components:
                components.append("carry_on_top")
        if self._bool(props.get("disappear_on_stand")):
            components.append("disappear_on_stand")
        if self._bool(props.get("breakable")):
            components.append("breakable")
        if props.get("signal_id") not in (None, "", 0, False):
            components.append("signal_toggle")
        return components

    def load_platforms(self, data, parallax, offset, ctx, layer_name, viewport_center):
        for obj in data.get("objects", []):
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)

            obj_props = props_list_to_dict(obj.get("properties", []))
            props = dict(self.platform_defaults)
            props.update(obj_props)

            path_ref = props.get("path")
            path_data = None
            if path_ref:
                path_data = ctx.references.get("paths_by_id", {}).get(int(path_ref))

            props["path_points"] = path_data["points"] if path_data else None
            props["path_closed"] = path_data.get("closed", False) if path_data else False

            if path_data:
                path_props = path_data.get("props", {}) or {}
                for key, value in path_props.items():
                    if key not in props or props[key] in (None, ""):
                        props[key] = value

            if props.get("path_points"):
                props["move"] = True
                props["move_type"] = "path"

            platform = ComponentPlatform(
                object_position,
                self.game_objects,
                components=self._components_from_flags(props),
                **props,
            )
            self.game_objects.platforms.add(platform)

    def load_paths(self, data, parallax, offset, ctx, viewport_center):
        ctx.references.setdefault("paths_by_id", {})

        for obj in data.get("objects", []):
            if "polyline" not in obj and "polygon" not in obj:
                continue

            base_pos = shape_object_position(obj, parallax, offset, viewport_center)
            points = obj.get("polyline") or obj.get("polygon")
            world_points = [(base_pos[0] + point["x"], base_pos[1] + point["y"]) for point in points]

            ctx.references["paths_by_id"][obj["id"]] = {
                "points": world_points,
                "closed": "polygon" in obj,
                "name": obj.get("name", ""),
                "props": props_list_to_dict(obj.get("properties", [])),
            }
