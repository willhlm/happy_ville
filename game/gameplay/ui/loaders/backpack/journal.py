import pygame

from ..base_loader import BaseLoader


class JournalLoader(BaseLoader):
    PAGE_OBJECT_LAYER = "objects"
    PAGE_TILESET = "journal_UI"

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
        for obj in self.map_data.get(self.PAGE_OBJECT_LAYER, []):
            local_id = self.get_object_local_id(obj, self.PAGE_TILESET)
            if local_id is None:
                continue

            topleft_object_position = self.get_object_topleft(obj)

            if local_id == 0:
                self.image_pos = topleft_object_position
            elif local_id == 1:
                self.name_pos.append(topleft_object_position)
