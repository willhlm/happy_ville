import pygame
from gameplay.ui.components import *
from gameplay.ui.loaders.base_loader import BaseLoader
     
class DefaultOverlayLoader(BaseLoader):
    def __init__(self, game_objects, image, title='', text=''):
        super().__init__(game_objects)
        self.bg = game_objects.game.display.surface_to_texture(
            pygame.image.load('assets/ui_layouts/overlay/items/bg.png').convert_alpha()
        )
        self.images = []
        path = 'assets/ui_layouts/overlay/items/items.json'
        self.load_UI_data(path, 'items')
        self.load_data(image, title, text)

    def load_data(self, image, title, text):
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']), int(obj['height'])]
            topleft_object_position = self.get_object_topleft(obj)
            local_id = self.get_object_local_id(obj, 'items_UI')
            
            if local_id == 11:
                if image is not None:
                    self.images.append(Image(self.game_objects, image, topleft_object_position, object_size))

        if not self.text_fields:
            raise ValueError("DefaultOverlayLoader requires shared text fields in the layout")

        if 'title' in self.text_fields:
            if title == '':
                raise ValueError("DefaultOverlayLoader layout requires a title text field, but no title was provided")
            self.assign_text_field('title', title)

        if 'text' in self.text_fields:
            if text == '':
                raise ValueError("DefaultOverlayLoader layout requires a text text field, but no text was provided")
            self.assign_text_field('text', text)
