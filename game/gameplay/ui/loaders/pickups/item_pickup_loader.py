import pygame
from gameplay.ui.components import *
from gameplay.ui.loaders.base_loader import BaseLoader
     
class ItemPickupLoader(BaseLoader):
    def __init__(self, game_objects, image, text):
        super().__init__(game_objects)
        self.bg = game_objects.game.display.surface_to_texture(
            pygame.image.load('assets/ui_layouts/pickups/items/bg.png').convert_alpha()
        )
        self.images = []
        path = 'assets/ui_layouts/pickups/items/items.json'
        self.load_UI_data(path, 'items')
        self.load_data(image, text)

    def load_data(self, image, text):
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']), int(obj['height'])]
            topleft_object_position = self.get_object_topleft(obj)
            local_id = self.get_object_local_id(obj, 'items_UI')
            
            if local_id == 11:
                if image is not None:
                    self.images.append(Image(self.game_objects, image, topleft_object_position, object_size))

        if not self.texts:
            raise ValueError("ItemPickupLoader requires a shared text object in the layout")
        self.texts[0].text = text
 
