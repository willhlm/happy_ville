import pygame

from ..base_loader import BaseLoader


class _VendorSlot:
    def __init__(self, position, size):
        self.rect = pygame.Rect(position, size)


class VendorLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/facilities/vendor/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/facilities/vendor/vendor.json"
        self.load_UI_data(path, "vendor")
        self.load_data()

    def load_data(self):
        self.objects = []
        self.next_items = []
        for obj in self.map_data["elements"]:
            object_size = [int(obj["width"]), int(obj["height"])]
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 0:
                self.amber = _VendorSlot(topleft_object_position, object_size)
            elif id == 1:
                self.objects.append(_VendorSlot(topleft_object_position, object_size))
            elif id == 2:
                self.description = {"position": topleft_object_position, "size": object_size}
            elif id == 3:
                self.next_items.append(_VendorSlot(topleft_object_position, object_size))
