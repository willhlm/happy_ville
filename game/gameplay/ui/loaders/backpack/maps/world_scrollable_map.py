from gameplay.ui.components import Banner

from .base_scrollable_map import BaseScrollableMapLoader


class ScrollableWorldMapLoader(BaseScrollableMapLoader):
    MARKER_TILESET = "map_markers"

    def __init__(self, game_objects):
        super().__init__(game_objects, folder="worldmap", tiled_name="worldmap")
        self.load_data()

    def load_data(self):
        self.markers = self.load_markers()
        self.ui_elements = self.shared_objects
        self.objects = self.markers

    def load_markers(self):
        markers = []
        for obj in self.map_data.get("markers", []):
            local_id = self.get_object_local_id(obj, self.MARKER_TILESET)
            if local_id is None:
                continue

            if local_id in (0, 1, 2):
                topleft_object_position = self.get_object_topleft(obj)
                properties = self.get_object_properties(obj)
                map_text = properties.get("text") or properties.get("map") or obj.get("name")
                markers.append(
                    Banner(
                        topleft_object_position,
                        self.game_objects,
                        str(local_id + 1),
                        map_text,
                    )
                )

        return markers
