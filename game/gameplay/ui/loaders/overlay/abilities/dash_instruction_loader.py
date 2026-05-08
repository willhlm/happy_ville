import pygame
from gameplay.ui.components import *
from gameplay.ui.loaders.base_loader import BaseLoader
     
class DashInstructionLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.bg = game_objects.game.display.surface_to_texture(
            pygame.image.load('assets/ui_layouts/overlay/abilities/dash/bg.png').convert_alpha()
        )
        path = 'assets/ui_layouts/overlay/abilities/dash/dash.json'
        self.load_UI_data(path, 'dash')
        self.load_data()

    def load_data(self):
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']), int(obj['height'])]
            topleft_object_position = self.get_object_topleft(obj)
            properties = self.get_object_properties(obj)
            local_id = self.get_object_local_id(obj, 'dash_UI')

            if local_id == 4:
                self.buttons['a'] = Controllers(
                    topleft_object_position,
                    self.game_objects,
                    'a',
                    self.game_objects.controller.controller_type[-1],
                )
            elif local_id == 5:
                self.buttons['b'] = Controllers(
                    topleft_object_position,
                    self.game_objects,
                    'b',
                    self.game_objects.controller.controller_type[-1],
                )
            elif local_id == 6:
                self.buttons['lb'] = Controllers(
                    topleft_object_position,
                    self.game_objects,
                    'lb',
                    self.game_objects.controller.controller_type[-1],
                )
            elif local_id == 7:
                self.buttons['rb'] = Controllers(
                    topleft_object_position,
                    self.game_objects,
                    'rb',
                    self.game_objects.controller.controller_type[-1],
                )
            elif local_id == 10:
                self.register_text_field(
                    Text(
                        self.game_objects,
                        properties['text'],
                        topleft_object_position,
                        size=object_size,
                    )
                )
 
