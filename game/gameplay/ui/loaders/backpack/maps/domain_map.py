from gameplay.ui.components import MapArrow

from .base_scrollable_map import BaseScrollableMapLoader

class DomainMapLoader(BaseScrollableMapLoader):
    SHARED_FOLDER = "local_map"
    SHARED_TILED_NAME = "local_map"
    MARKER_TILESET = "map_markers"

    def __init__(self, game_objects):
        super().__init__(game_objects, folder=self.SHARED_FOLDER, tiled_name=self.SHARED_TILED_NAME)
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

            if local_id in (0, 1):
                properties = self.get_object_properties(obj)
                direction = properties.get("direction")
                if not direction:
                    continue

                topleft_object_position = self.get_object_topleft(obj)
                markers.append(
                    MapArrow(
                        topleft_object_position,
                        self.game_objects,
                        properties.get("map"),
                        direction,
                    )
                )

        return markers
