import pygame

from ..base_loader import BaseLoader


class FastTravelLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/facilities/fast_travel/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/facility/fast_travel/fast_travel.json"
        self.load_UI_data(path, "fast_travel")
        self.load_data()

    def load_data(self):
        self.name_pos = []
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 0:
                self.name_pos.append(topleft_object_position)
