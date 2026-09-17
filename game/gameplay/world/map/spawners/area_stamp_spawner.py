from . import common as c


class AreaStampSpawner(c.SpawnerCommon):
    def load_area_stamps(self, data, parallax, offset, map_def: c.MapDefinition, viewport_center):
        for obj in data["objects"]:
            source, _, local_id = c.resolve_tileset(map_def, obj["gid"])
            if source is None or "static_stamps" not in source:
                continue

            object_position, object_size = c.calculate_object_position(obj, parallax, offset, viewport_center)
            
            if local_id == 14:                        
                mode = "center"
                camera_offset = 0
                priority = 0
                for property in obj.get("properties", []):
                    if property["name"] in ("direction", "mode"):
                        mode = property["value"]
                    elif property["name"] == "offset":
                        camera_offset = property["value"]
                    elif property["name"] == "priority":
                        priority = property["value"]
                self.game_objects.camera_blocks.add(
                    c.CameraStop(self.game_objects, object_size, object_position, mode, camera_offset, priority)
                )
