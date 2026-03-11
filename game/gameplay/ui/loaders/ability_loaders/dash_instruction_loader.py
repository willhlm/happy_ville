import pygame
from gameplay.ui.components import *
from gameplay.ui.loaders import BaseLoader
     
class DashInstructionLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.bg = game_objects.game.display.surface_to_texture(pygame.image.load('assets/ui_layouts/abilities/dash/bg.png').convert_alpha())    
        path = 'assets/ui_layouts/abilities/dash/dash.json'
        self.load_UI_data(path, 'dash')
        self.load_data()

    def load_data(self):
        self.buttons = []
        self.text = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']
            
            if id == 4:#a button
                new_button = Controllers(topleft_object_position,self.game_objects,'a', self.game_objects.controller.controller_type[-1])
                self.buttons.append(new_button)
            elif id == 5:#b button
                new_button = Controllers(topleft_object_position,self.game_objects,'b', self.game_objects.controller.controller_type[-1])
                self.buttons.append(new_button)
            elif id == 6:#lb button
                new_button = Controllers(topleft_object_position,self.game_objects,'lb', self.game_objects.controller.controller_type[-1])
                self.buttons.append(new_button)
            elif id == 7:#rb button
                new_button = Controllers(topleft_object_position,self.game_objects,'rb', self.game_objects.controller.controller_type[-1])
                self.buttons.append(new_button)

            elif id == 10:#text
                for property in properties:
                    if property['name'] == 'text':
                        text = property['value']

                new_text = Text(self.game_objects, text, topleft_object_position, size = object_size)
                self.text.append(new_text)                
 