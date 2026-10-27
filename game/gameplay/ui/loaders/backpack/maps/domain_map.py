from gameplay.ui.components import MapArrow, MapPin

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
        self.ui_elements = [
            element
            for element in self.shared_elements
            if element not in self.controller_prompts.values()
        ]
        self.objects = self.markers

    def load_markers(self):
        markers = []
        for obj in self.map_data.get("markers", []):
            local_id = self.get_object_local_id(obj, self.MARKER_TILESET)
            if local_id is None:
                continue

            properties = self.get_object_properties(obj)
            topleft_object_position = self.get_object_topleft(obj)

            if local_id == 1:
                direction = properties.get("direction")
                if not direction:
                    continue

                marker = MapArrow(
                    topleft_object_position,
                    self.game_objects,
                    properties.get("map"),
                    direction,
                )
                markers.append(
                    self.configure_marker(marker, properties)
                )

            elif local_id == 2:
                sprite_path = "assets/sprites/ui/menus/map/pins/save_point/Sprite-0001.png"
                properties.setdefault("visibility", "unlocked")
                properties.setdefault("selectable", True)

                if not properties.get("room_id"):
                    marker_center = (topleft_object_position[0] + int(obj["width"]) * 0.5, topleft_object_position[1] + int(obj["height"]) * 0.5)
                    properties["room_id"] = next((room_id for room_id, locator in self.locator_areas.items() if locator.collidepoint(marker_center)), None)

                if not properties.get("marker_id"):
                    properties["marker_id"] = properties.get("room_id")

                save_point_pin = MapPin(topleft_object_position, self.game_objects, sprite_path)
                markers.append(self.configure_marker(save_point_pin, properties))

        return markers
