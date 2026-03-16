import pygame

from gameplay.ui.components import Banner

from ...base_loader import BaseLoader


class WorldMapLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/backpack/maps/worldmap/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/backpack/maps/worldmap/worldmap.json"
        self.load_UI_data(path, "worldmap")
        self.load_data()

    def load_data(self):
        self.objects = []
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id in (0, 1, 2):
                banner = Banner(topleft_object_position, self.game_objects, str(id + 1), properties[0]["value"])
                self.objects.append(banner)
