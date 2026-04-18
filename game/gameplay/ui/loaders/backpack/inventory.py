import pygame

from gameplay.ui.components import Controllers, InventoryContainer, Sword

from ..base_loader import BaseLoader


class InventoryLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/backpack/inventory/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/backpack/inventory/inventory.json"
        self.load_UI_data(path, "inventory")
        self.load_data()

    def load_data(self):
        self.buttons = {}
        self.containers = []
        self.items = {}
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 0:
                self.items["sword"] = Sword(topleft_object_position, self.game_objects)
            elif id == 4:
                self.buttons["a"] = Controllers(
                    topleft_object_position, self.game_objects, "a", self.game_objects.controller.controller_type[-1]
                )
            elif id == 5:
                self.buttons["b"] = Controllers(
                    topleft_object_position, self.game_objects, "b", self.game_objects.controller.controller_type[-1]
                )
            elif id == 6:
                self.buttons["lb"] = Controllers(
                    topleft_object_position, self.game_objects, "lb", self.game_objects.controller.controller_type[-1]
                )
            elif id == 7:
                self.buttons["rb"] = Controllers(
                    topleft_object_position, self.game_objects, "rb", self.game_objects.controller.controller_type[-1]
                )
            elif id == 10:
                item = str(obj["id"])
                for property in properties:
                    if property["name"] == "item":
                        item = property["value"]
                self.containers.append(InventoryContainer(topleft_object_position, self.game_objects, item))
            elif id == 11:
                self.items["amberdroplet"] = topleft_object_position
            elif id == 12:
                self.items["bone"] = topleft_object_position
            elif id == 13:
                self.items["healitem"] = topleft_object_position
