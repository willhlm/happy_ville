import pygame

from gameplay.ui.components import Hand, InventoryContainer

from ..base_loader import BaseLoader


class RadnaLoader(BaseLoader):
    PAGE_OBJECT_LAYER = "objects"
    PAGE_TILESET = "radna_UI"

    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(
            pygame.image.load("assets/ui_layouts/backpack/radna/BG.png").convert_alpha()
        )
        path = "assets/ui_layouts/backpack/radna/radna.json"
        self.load_UI_data(path, "radna")
        self.load_data()

    def load_data(self):
        self.containers = []
        self.equipped_containers = {}
        self.items = {}
        self.rings = {}
        for obj in self.map_data.get(self.PAGE_OBJECT_LAYER, []):
            local_id = self.get_object_local_id(obj, self.PAGE_TILESET)
            if local_id is None:
                continue

            topleft_object_position = self.get_object_topleft(obj)
            item = self.get_object_properties(obj).get("item", str(obj["id"]))

            if local_id == 0:
                self.items["hand"] = Hand(topleft_object_position, self.game_objects)
            elif local_id == 1:
                if item in ["index", "long", "ring", "small"]:
                    self.equipped_containers[item] = InventoryContainer(topleft_object_position, self.game_objects, item)
                else:
                    self.containers.append(InventoryContainer(topleft_object_position, self.game_objects, item))
            elif local_id == 2:
                self.items["half_dmg"] = topleft_object_position
            elif local_id == 3:
                self.rings["index"] = topleft_object_position
            elif local_id == 5:
                self.items["boss_hp"] = topleft_object_position
            elif local_id == 6:
                self.items["loot_magnet"] = topleft_object_position
            elif local_id == 7:
                self.rings["long"] = topleft_object_position
            elif local_id == 8:
                self.rings["ring"] = topleft_object_position
            elif local_id == 9:
                self.rings["small"] = topleft_object_position
