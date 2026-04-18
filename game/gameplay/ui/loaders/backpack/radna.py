import pygame

from gameplay.ui.components import Hand, InventoryContainer

from ..base_loader import BaseLoader


class RadnaLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/backpack/radna/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/backpack/radna/radna.json"
        self.load_UI_data(path, "radna")
        self.load_data()

    def load_data(self):
        self.buttons = {}
        self.containers = []
        self.equipped_containers = {}
        self.items = {}
        self.rings = {}
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 0:
                self.items["hand"] = Hand(topleft_object_position, self.game_objects)
            elif id == 1:
                item = str(obj["id"])
                for property in properties:
                    if property["name"] == "item":
                        item = property["value"]

                if item in ["index", "long", "ring", "small"]:
                    self.equipped_containers[item] = InventoryContainer(topleft_object_position, self.game_objects, item)
                else:
                    self.containers.append(InventoryContainer(topleft_object_position, self.game_objects, item))
            elif id == 2:
                self.items["half_dmg"] = topleft_object_position
            elif id == 3:
                self.rings["index"] = topleft_object_position
            elif id == 7:
                self.rings["long"] = topleft_object_position
            elif id == 8:
                self.rings["ring"] = topleft_object_position
            elif id == 9:
                self.rings["small"] = topleft_object_position
            elif id == 5:
                self.items["boss_hp"] = topleft_object_position
            elif id == 6:
                self.items["loot_magnet"] = topleft_object_position
