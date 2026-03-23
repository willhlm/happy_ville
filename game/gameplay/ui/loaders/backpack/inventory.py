import pygame

from gameplay.ui.components import InventoryContainer, Sword

from ..base_loader import BaseLoader


class InventoryLoader(BaseLoader):
    PAGE_TILESET = "inventory_UI"
    PAGE_OBJECT_LAYER = "objects"

    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load("assets/ui_layouts/backpack/inventory/BG.png").convert_alpha())
        path = "assets/ui_layouts/backpack/inventory/inventory.json"
        self.load_UI_data(path, "inventory")
        self.load_data()

    def load_data(self):        
        self.containers = []
        self.items = {}
        for obj in self.map_data.get(self.PAGE_OBJECT_LAYER, []):
            local_id = self.get_object_local_id(obj, self.PAGE_TILESET)
            if local_id is None:
                continue

            topleft_object_position = self.get_object_topleft(obj)
            properties = self.get_object_properties(obj)

            if local_id == 0:
                self.items["sword"] = Sword(topleft_object_position, self.game_objects)
            elif local_id == 10:
                item = properties.get("item", str(obj["id"]))
                self.containers.append(InventoryContainer(topleft_object_position, self.game_objects, item))
            elif local_id == 11:
                self.items["amberdroplet"] = topleft_object_position
            elif local_id == 12:
                self.items["bone"] = topleft_object_position
            elif local_id == 13:
                self.items["healitem"] = topleft_object_position
