import pygame
import read_files
import entities_UI

class UI_loader():#for map, omamori, ability, journal etc: json file should have same name as class and folder, tsx file should end with _UI
    def __init__(self, game_objects):
        self.game_objects = game_objects
        type = self.__class__.__name__.lower()
        self.BG = game_objects.game.display.surface_to_texture(pygame.image.load('UI/' + type + '/BG.png').convert_alpha())
        self.load_UI_data(type)
        self.load_data()

    def load_UI_data(self, type):
        map_data = read_files.read_json("UI/%s/%s.json" % (type,type))
        self.map_data = read_files.format_tiled_json(map_data)
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if type + '_UI' in tileset['source']:#the name of the tmx file
                    self.map_data['UI_firstgid'] =  tileset['firstgid']

class Vendor(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def load_data(self):
        self.objects = []
        self.next_items = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#amber position
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)#shuold change from Item to a UI amber
                self.amber = new_item
            elif id == 1:#sell item position
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)
                self.objects.append(new_item)
            elif id == 2:#the description box posiiton
                self.description = {'position': topleft_object_position, 'size' : object_size}
            elif id == 3:#the items showing what's next
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)
                self.next_items.append(new_item)

class Map(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def load_data(self):
        self.objects = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:
                new_banner = entities_UI.Banner(topleft_object_position,self.game_objects,str(1),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 1:
                new_banner = entities_UI.Banner(topleft_object_position,self.game_objects,str(2),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 2:
                new_banner = entities_UI.Banner(topleft_object_position,self.game_objects,str(3),properties[0]['value'])
                self.objects.append(new_banner)

class Omamori(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def load_data(self):
        self.equipped = []
        self.inventory = {}
        for index, obj in enumerate(self.map_data['elements']):
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#inventory
                if properties:
                    name = properties[0]['value']#the name of omamori
                else:
                    name = str(index)
                new_omamori = entities_UI.Omamori(topleft_object_position,self.game_objects)
                self.inventory[name] = new_omamori
            elif id == 1:#equipeed
                new_omamori = entities_UI.Omamori(topleft_object_position,self.game_objects)
                self.equipped.append(new_omamori)
            elif id == 2:#necklace
                self.necklace = entities_UI.Necklace(topleft_object_position,self.game_objects)

        self.equipped.sort(key = lambda x: x.rect.centery)#sort the order according to left to right

class Journal(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)

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

    def load_data(self):
        self.key_items = {}
        self.items = []
        self.stones = {}
        self.buttons = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#sword
                new_item = entities_UI.Sword(topleft_object_position,self.game_objects)
                self.sword = new_item
            elif id == 1:#infinity stone
                name = properties[0]['value']#the name of stone
                new_item = entities_UI.Infinity_stone(topleft_object_position,self.game_objects)#make an object based on stringgetattr(entities_UI, name)
                self.stones[name] = new_item
            elif id == 2:#item
                name = properties[0]['value']#the name of item
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)
                self.items.append(new_item)
            elif id == 3:#key_item
                name = properties[0]['value']#the name of keyitem
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)
                self.key_items[name] = new_item
            elif id == 4:#a button
                new_button = getattr(entities_UI, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'a')
                self.buttons['a'] = new_button
            elif id == 5:#b button
                new_button = getattr(entities_UI, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'b')
                self.buttons['b'] = new_button
            elif id == 6:#lb button
                new_button = getattr(entities_UI, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'lb')
                self.buttons['lb'] = new_button
            elif id == 7:#rb button
                new_button = getattr(entities_UI, self.game_objects.controller.controller_type[-1].capitalize())(topleft_object_position,self.game_objects,'rb')
                self.buttons['rb'] = new_button
            elif id == 8:#item
                name = properties[0]['value']#the name of item
                new_item = entities_UI.Item_new(topleft_object_position,self.game_objects)
                self.items.append(new_item)

class Ability_movement_upgrade(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def load_data(self):
        self.abilities = [[],[],[]]#orginise them accotding to the grid in tiled
        self.rows = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#dash
                new_ability = entities_UI.Dash(topleft_object_position,self.game_objects)
                self.abilities[0].append(new_ability)
                self.rows['Dash'] = 0
            elif id == 1:#double_jump
                new_ability = entities_UI.Double_jump(topleft_object_position,self.game_objects)
                self.abilities[1].append(new_ability)
                self.rows['Double_jump'] = 1
            elif id == 2:#wall_glide
                new_ability = entities_UI.Wall_glide(topleft_object_position,self.game_objects)
                self.abilities[2].append(new_ability)
                self.rows['Wall_glide'] = 2

class Ability_spirit_upgrade(UI_loader):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def load_data(self):
        self.abilities = [[],[],[],[],[]]#orginise them accotding to the grid in tiled
        self.rows = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#arrow
                new_ability = entities_UI.Arrow(topleft_object_position,self.game_objects)
                self.abilities[0].append(new_ability)
                self.rows['Arrow'] = 0
            elif id == 1:#force
                new_ability = entities_UI.Force(topleft_object_position,self.game_objects)
                self.abilities[1].append(new_ability)
                self.rows['Force'] = 1
            elif id == 2:#migawari
                new_ability = entities_UI.Migawari(topleft_object_position,self.game_objects)
                self.abilities[2].append(new_ability)
                self.rows['Migawari'] = 2
            elif id == 3:#slowmotion
                new_ability = entities_UI.Slow_motion(topleft_object_position,self.game_objects)
                self.abilities[3].append(new_ability)
                self.rows['Slow_motion'] = 3
            elif id == 4:#thunder
                new_ability = entities_UI.Thunder(topleft_object_position,self.game_objects)
                self.abilities[4].append(new_ability)
                self.rows['Thunder'] = 4
