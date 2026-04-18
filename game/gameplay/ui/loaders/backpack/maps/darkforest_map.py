import pygame

from gameplay.ui.components import MapArrow

from ...base_loader import BaseLoader


class DarkforestMapLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/backpack/maps/darkforest/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/backpack/maps/darkforest/darkforest.json"
        self.load_UI_data(path, "darkforest")
        self.load_data()

    def load_data(self):
        self.objects = []
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 0:
                direction = None
                map_name = None
                for property in properties:
                    if property["name"] == "direction":
                        direction = property["value"]
                    elif property["name"] == "map":
                        map_name = property["value"]
                self.objects.append(MapArrow(topleft_object_position, self.game_objects, map_name, direction))
