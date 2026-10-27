import pygame

from ...base_loader import BaseLoader


class BaseScrollableMapLoader(BaseLoader):
    # Tiled convention for maps:
    # - Use an object layer named "shared" for shared UI objects from assets/ui_layouts/shared.tsx.
    #   Shared map objects use the shared tileset
    # - Use an object layer named "markers" for map-specific markers such as banners or local arrows.
    #   Marker objects should use the marker tileset and carry the properties required
    #   by that marker type
    # - Use object layers like "rooms" / "room_mask" / "reveal" for reveal polygons and rectangles.
    #   Local reveal objects should include a "room_id" property matching the full room name.
    #   World-map reveal objects may instead use "domain_id".
    # - An optional "locators" object layer can provide one positioning rectangle per room.
    #   Without one, the largest reveal shape for that room is used. Explicit locators are useful
    #   when reveal geometry includes corridors or has a shape that should not control positioning.
    # - Local/domain maps load the full map data and scrolling only changes which part of
    #   that map is visible. Visibility is controlled by room discovery via the reveal layers.
    # - Keep the map background in BG.png and the map json inside assets/ui_layouts/backpack/maps/<folder>/.
    REVEAL_LAYER_NAMES = {"reveal", "reveals", "reveal_mask", "mask", "room", "rooms", "room_mask", "room_masks"}
    LOCATOR_LAYER_NAMES = {"locator", "locators", "player_locator", "player_locators"}
    SHARED_OBJECT_LAYER = "shared"
    SHARED_TILESET = BaseLoader.DEFAULT_SHARED_TILESET

    def __init__(self, game_objects, *, folder, tiled_name):
        super().__init__(game_objects)
        self.folder = folder
        self.tiled_name = tiled_name
        self.base_path = f"assets/ui_layouts/backpack/maps/{folder}"
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load(f"{self.base_path}/BG.png").convert_alpha())
        self.load_UI_data(f"{self.base_path}/{tiled_name}.json", tiled_name)
        self.reveal_areas = self.load_reveal_areas()
        self.locator_areas = self.load_locator_areas()
        self.markers = []
        self.ui_elements = []
        self.objects = self.markers

    def load_reveal_areas(self):
        reveal_areas = {}
        for layer in self.raw_map_data.get("layers", []):
            layer_name = layer.get("name", "").lower()
            if layer.get("type") != "objectgroup":
                continue
            if layer_name not in self.REVEAL_LAYER_NAMES and not layer_name.startswith("reveal"):
                continue

            for obj in layer.get("objects", []):
                if not self.include_reveal_object(obj):
                    continue
                area_id = self._get_area_id(obj)
                if not area_id:
                    continue
                reveal_areas.setdefault(area_id, [])
                points = self._object_to_points(obj)
                if points:
                    reveal_areas[area_id].append(points)

        return reveal_areas

    def load_locator_areas(self):
        locator_areas = {}
        for layer in self.raw_map_data.get("layers", []):
            layer_name = layer.get("name", "").lower()
            if layer.get("type") != "objectgroup" or layer_name not in self.LOCATOR_LAYER_NAMES:
                continue

            for obj in layer.get("objects", []):
                area_id = self._get_area_id(obj)
                if not area_id:
                    continue

                width = int(obj.get("width", 0))
                height = int(obj.get("height", 0))
                if width <= 0 or height <= 0:
                    continue

                # Keep the first locator deterministic if an author accidentally duplicates one.
                locator_areas.setdefault(
                    area_id,
                    pygame.Rect(
                        int(obj.get("x", 0)),
                        int(obj.get("y", 0)),
                        width,
                        height,
                    ),
                )

        # Explicit locators override these fallbacks. Selecting the largest reveal
        # shape normally chooses the room body instead of a smaller attached corridor.
        for area_id, reveal_shapes in self.reveal_areas.items():
            if area_id in locator_areas:
                continue

            candidates = []
            for points in reveal_shapes:
                if not points:
                    continue
                left = min(point[0] for point in points)
                top = min(point[1] for point in points)
                right = max(point[0] for point in points)
                bottom = max(point[1] for point in points)
                width = right - left
                height = bottom - top
                if width > 0 and height > 0:
                    candidates.append(pygame.Rect(left, top, width, height))

            if candidates:
                locator_areas[area_id] = max(
                    candidates,
                    key=lambda rect: rect.width * rect.height,
                )

        return locator_areas

    def include_reveal_object(self, obj):
        return True

    def _get_area_id(self, obj):
        properties = self.get_object_properties(obj)
        area_id = (
            properties.get("room_id")
            or properties.get("domain_id")
            or properties.get("area_id")
            or properties.get("id")
            or properties.get("area")
            or obj.get("name")
            or obj.get("id")
        )
        if area_id is None:
            return None
        return str(area_id)

    def _object_to_points(self, obj):
        origin_x = float(obj.get("x", 0))
        origin_y = float(obj.get("y", 0))

        if "polygon" in obj:
            return [
                (int(origin_x + point["x"]), int(origin_y + point["y"]))
                for point in obj["polygon"]
            ]

        width = int(obj.get("width", 0))
        height = int(obj.get("height", 0))
        if width <= 0 or height <= 0:
            return []

        return [
            (int(origin_x), int(origin_y)),
            (int(origin_x + width), int(origin_y)),
            (int(origin_x + width), int(origin_y + height)),
            (int(origin_x), int(origin_y + height)),
        ]

    def configure_marker(self, marker, properties):
        """Attach map semantics without coupling markers to a future action system.

        SavePoints can later provide destination and spawn metadata while remaining
        ordinary selectable markers. The player marker is deliberately not part of
        this collection.
        """
        marker.room_id = (
            properties.get("room_id")
            or properties.get("domain_id")
            or properties.get("area_id")
        )
        marker.marker_id = (
            properties.get("marker_id")
            or properties.get("save_point_id")
        )
        marker.visibility = str(properties.get("visibility", "always")).lower()
        marker.selectable = bool(properties.get("selectable", True))
        marker.destination_map = properties.get("destination_map") or properties.get("map")
        marker.spawn_id = properties.get("spawn_id")
        marker.spawn_position = properties.get("spawn_position")
        marker.unlocked = bool(properties.get("unlocked", False))
        return marker
