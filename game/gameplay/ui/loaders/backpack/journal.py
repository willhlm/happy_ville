import pygame

from ..base_loader import BaseLoader


class JournalLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/backpack/journal/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/backpack/journal/journal.json"
        self.load_UI_data(path, "journal")
        self.load_data()

    def load_data(self):
        self.name_pos = []
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 0:
                self.image_pos = topleft_object_position
            elif id == 1:
                self.name_pos.append(topleft_object_position)
