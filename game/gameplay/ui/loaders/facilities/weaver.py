import pygame
from ..base_loader import BaseLoader
from gameplay.ui.components.menus.weaver.preview_player import PreviewPlayer
from gameplay.ui.components import InventoryContainer

class WeaverLoader(BaseLoader):
    PAGE_TILESET = "weaver_UI"
    PAGE_OBJECT_LAYER = "objects"

    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.bg = game_objects.game.display.surface_to_texture(pygame.image.load("assets/ui_layouts/facilities/weaver/BG.png").convert_alpha())
        self.categories = {}
        path = "assets/ui_layouts/facilities/weaver/weaver.json"
        self.load_UI_data(path, "weaver")
        self.load_data()        

    def load_data(self):        
        for obj in self.map_data.get(self.PAGE_OBJECT_LAYER, []):
            local_id = self.get_object_local_id(obj, self.PAGE_TILESET)
            if local_id is None: continue
                
            topleft_object_position = self.get_object_topleft(obj)
            properties = self.get_object_properties(obj)

            if local_id == 0:#aila
                self.player  = PreviewPlayer(topleft_object_position, self.game_objects)               

            elif local_id == 1:#category position
                category = properties['category']
                self.categories[category] = {
                    'container': InventoryContainer(topleft_object_position, self.game_objects, category),
                    'dye_key': properties.get('dye_key', category),
                    'dyes': [None],
                    'index': 0,
                }

    def assign_dyes(self, dyes):
        for entry in self.categories.values():
            entry['dyes'] = [None]
            entry['index'] = 0

        for dye in dyes:
            for entry in self.categories.values():
                if dye.type == entry['dye_key']:
                    entry['dyes'].append(dye)
                    break
