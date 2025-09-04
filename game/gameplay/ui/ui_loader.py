import pygame
from engine.utils import read_files
from gameplay.entities import entities_ui

class UI_loader():#for map, omamori, ability, journal etc: json file should have same name as class and folder, tsx file should end with _UI
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def load_UI_data(self, path, name):
        map_data = read_files.read_json(path)
        self.map_data = read_files.format_tiled_json(map_data)
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if name + '_UI' in tileset['source']:#the name of the tmx file
                    self.map_data['UI_firstgid'] =  tileset['firstgid']

    def load_data(self):
        pass

class Vendor(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/facilities/vendor/BG.png').convert_alpha())    
        path = 'assets/sprites/ui/layouts/facilities/vendor/vendor.json'
        self.load_UI_data(path, 'vendor')
        self.load_data()

    def load_data(self):
        self.objects = []
        self.next_items = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#amber position
                new_item = entities_ui.Item(topleft_object_position,self.game_objects)#shuold change from Item to a UI amber
                self.amber = new_item
            elif id == 1:#sell item position
                new_item = entities_ui.Item(topleft_object_position,self.game_objects)
                self.objects.append(new_item)
            elif id == 2:#the description box posiiton
                self.description = {'position': topleft_object_position, 'size' : object_size}
            elif id == 3:#the items showing what's next
                new_item = entities_ui.Item(topleft_object_position,self.game_objects)
                self.next_items.append(new_item)

class Radna(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/radna/BG.png').convert_alpha())    

        path = 'assets/sprites/ui/layouts/backpack/radna/radna.json'
        self.load_UI_data(path, 'radna')
        self.load_data()

    def load_data(self):
        self.buttons = {}
        self.containers = []
        self.equipped_containers = {}
        self.items = {}
        self.rings = {}
        for index, obj in enumerate(self.map_data['elements']):
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#inventory
                self.items['hand'] = entities_ui.Hand(topleft_object_position,self.game_objects)

            elif id == 1:#Container
                item = str(obj['id'])
                for property in properties:
                    if property['name'] == 'item':
                        item = property['value']
                
                if item in ['index', 'long', 'ring', 'small']:#name of the fingers
                    self.equipped_containers[item] = entities_ui.InventoryContainer(topleft_object_position, self.game_objects, item)
                else:
                    self.containers.append(entities_ui.InventoryContainer(topleft_object_position, self.game_objects, item))

            elif id == 2:#haöf_dmg
                self.items['half_dmg'] = topleft_object_position

            elif id == 3:#base ring        
                self.rings['index'] = topleft_object_position
            elif id == 7:#base ring        
                self.rings['long'] = topleft_object_position
            elif id == 8:#base ring        
                self.rings['ring'] = topleft_object_position
            elif id == 9:#base ring        
                self.rings['small'] = topleft_object_position

            elif id == 5:#boss hp
                self.items['boss_hp'] = topleft_object_position

            elif id == 6:#Loot_magnet
                self.items['loot_magnet'] = topleft_object_position

class Journal(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/journal/BG.png').convert_alpha())            
        path = 'assets/sprites/ui/layouts/backpack/journal/journal.json'
        self.load_UI_data(path, 'journal')
        self.load_data()

    def load_data(self):
        self.name_pos = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#image
                self.image_pos = topleft_object_position
            elif id == 1:#name
                self.name_pos.append(topleft_object_position)

class Fast_travel(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/facilities/fast_travel/BG.png').convert_alpha())                    
        path = 'assets/sprites/ui/layouts/facility/fast_travel/fast_travel.json'
        self.load_UI_data(path, 'fast_travel')
        self.load_data()

    def load_data(self):
        self.name_pos = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#name
                self.name_pos.append(topleft_object_position)

class Inventory(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/inventory/BG.png').convert_alpha())                    
        path = 'assets/sprites/ui/layouts/backpack/inventory/inventory.json'
        self.load_UI_data(path, 'inventory')
        self.load_data()

    def load_data(self):
        self.buttons = {}
        self.containers = []
        self.items = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#sword
                self.items['sword'] = entities_ui.Sword(topleft_object_position,self.game_objects)

            elif id == 4:#a button
                new_button = getattr(entities_ui, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'a')
                self.buttons['a'] = new_button
            elif id == 5:#b button
                new_button = getattr(entities_ui, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'b')
                self.buttons['b'] = new_button
            elif id == 6:#lb button
                new_button = getattr(entities_ui, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'lb')
                self.buttons['lb'] = new_button
            elif id == 7:#rb button
                new_button = getattr(entities_ui, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'rb')
                self.buttons['rb'] = new_button

            elif id == 10:#Container
                item = str(obj['id'])
                for property in properties:
                    if property['name'] == 'item':
                        item = property['value']
                self.containers.append(entities_ui.InventoryContainer(topleft_object_position, self.game_objects, item))

            elif id == 11:#money
                self.items['amber_droplet'] = topleft_object_position
            elif id == 12:#bone
                self.items['bone'] = topleft_object_position
            elif id == 13:#heal item
                self.items['heal_item'] = topleft_object_position

class TitleMenu(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/images/menus/title_menu/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/music/load_screen/')

        path = 'assets/sprites/ui/layouts/menus/title_menu/title_menu.json'
        self.load_UI_data(path, 'title_menu')
        self.load_data()

    def load_data(self):
        self.buttons = []
        self.arrows = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#buttons
                for property in properties:
                    if property['name'] == 'name':
                        button = property['value']

                text = (self.game_objects.font.render(text = button))
                self.buttons.append(entities_ui.Button(self.game_objects, image = text, position = topleft_object_position, center = True))

            elif id == 1:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects, flip = True))

            elif id == 4:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects))

class LoadMenu(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/images/menus/load_menu/', game_objects)

        path = 'assets/sprites/ui/layouts/menus/load_menu/load_menu.json'
        self.load_UI_data(path, 'load_menu')
        self.load_data()

    def load_data(self):
        self.buttons = []
        self.arrows = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#buttons
                for property in properties:
                    if property['name'] == 'name':
                        button = property['value']

                text = (self.game_objects.font.render(text = button))
                self.buttons.append(entities_ui.Button(self.game_objects, image = text, position = topleft_object_position, center = True))

            elif id == 1:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects, flip = True))

            elif id == 4:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects))

class OptionMenu(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/images/menus/option_menu/', game_objects)

        path = 'assets/sprites/ui/layouts/menus/option_menu/option_menu.json'
        self.load_UI_data(path, 'option_menu')
        self.load_data()

    def load_data(self):
        self.buttons = []
        self.arrows = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#buttons
                for property in properties:
                    if property['name'] == 'name':
                        button = property['value']

                text = (self.game_objects.font.render(text = button))
                self.buttons.append(entities_ui.Button(self.game_objects, image = text, position = topleft_object_position, center = True))

            elif id == 1:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects, flip = True))

            elif id == 4:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects))

class PauseMenu(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = 'assets/sprites/ui/layouts/menus/pause_menu/pause_menu.json'
        self.load_UI_data(path, 'pause_menu')
        self.load_data()

    def load_data(self):
        self.buttons = []
        self.arrows = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#buttons
                for property in properties:
                    if property['name'] == 'name':
                        button = property['value']

                text = (self.game_objects.font.render(text = button))
                self.buttons.append(entities_ui.Button(self.game_objects, image = text, position = topleft_object_position, center = True))

            elif id == 1:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects, flip = True))

            elif id == 4:#arrows
                self.arrows.append(entities_ui.MenuArrow(topleft_object_position, self.game_objects))

class WorldMap(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/maps/worldmap/BG.png').convert_alpha())
        path = 'assets/sprites/ui/layouts/backpack/maps/worldmap/worldmap.json'
        self.load_UI_data(path, 'worldmap')
        self.load_data()

    def load_data(self):
        self.objects = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:
                new_banner = entities_ui.Banner(topleft_object_position,self.game_objects,str(1),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 1:
                new_banner = entities_ui.Banner(topleft_object_position,self.game_objects,str(2),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 2:
                new_banner = entities_ui.Banner(topleft_object_position,self.game_objects,str(3),properties[0]['value'])
                self.objects.append(new_banner)

class NordvedenMap(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/maps/nordveden/BG.png').convert_alpha())
        self.objects = []
        path = 'assets/sprites/ui/layouts/backpack/maps/nordveden/nordveden.json'
        self.load_UI_data(path, 'nordveden')
        self.load_data()

    def load_data(self):
        self.objects = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:
                for property in properties:
                    if property['name'] == 'direction':
                        direction = property['value']
                    elif property['name'] == 'map':
                        map = property['value']

                new_arrow = entities_ui.MapArrow(topleft_object_position, self.game_objects, map, direction)
                self.objects.append(new_arrow)

class DarkforestMap(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/maps/darkforest/BG.png').convert_alpha())
        self.objects = []
        path = 'assets/sprites/ui/layouts/backpack/maps/darkforest/darkforest.json'
        self.load_UI_data(path, 'darkforest')
        self.load_data()

    def load_data(self):
        self.objects = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:
                for property in properties:
                    if property['name'] == 'direction':
                        direction = property['value']
                    elif property['name'] == 'map':
                        map = property['value']

                new_arrow = entities_ui.MapArrow(topleft_object_position, self.game_objects, map, direction)
                self.objects.append(new_arrow)

class HlifblomMap(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('assets/sprites/ui/layouts/backpack/maps/hlifblom/BG.png').convert_alpha())
        self.objects = []