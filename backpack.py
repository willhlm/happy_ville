class Backpack():#Ailas back pack. Can append new things such as journal, if picked up
    def __init__(self, entity):
        self.holdings = {'map': Map(), 'inventory': Inventory(), 'necklace': Necklace(entity), 'journal': Journal()}
        
    @property
    def inventory(self):
        return self.holdings['inventory']

    @property
    def map(self):
        return self.holdings['map']

    @property
    def necklace(self):
        return self.holdings['necklace']        

    @property
    def journal(self):
        return self.holdings['journal']    

class Inventory():
    def __init__(self):
        self.items = {}  # Stores items and their quantities

    def add(self, item, quantity = 1):  # Allow adding multiple at once
        item_name = type(item).__name__.lower()
        self.items.setdefault(item_name, {'item': item, 'quantity': 0})
        self.items[item_name]['quantity'] += quantity

    def remove(self, item_name, quantity = 1):
        self.items[item_name]['quantity'] -= quantity
    
    def get_quantity(self, item_name):#return quantity. If item doesn't exist, return 0
        return self.items.get(item_name, {}).get('quantity', 0)

class Map():        
    def __init__(self):
        self.spawn_point = {'map': 'nordveden_1', 'point': '1', 'safe_spawn' : [0,0]}#can append bone
        self.travel_points = {}#Fast travel system will read this dict. The key is the map, value is the coordinate. Appends the info when the travel is unlocked
        self.visited_bioms = {}#should be filled when nwe biome is visited

    def new_biome(self, biome):#called when a new biome is visited
        self.visited_bioms[biome] = True

    def save_savepoint(self, map, point):#called when interact with savepoint
        self.spawn_point['map'] = map
        self.spawn_point['point'] = point

    def save_safespawn(self, coordinate):#called wheb collliding with safe spawn
        self.spawn_point['safe_spawn'] = coordinate

    def save_bone(self, map, point):#called when plaiting a bone
        self.spawn_point['bone'] = {'map':self.game_objects.map.level_name, 'point':self.game_objects.camera_manager.camera.scroll}     

    def save_travelpoint(self, map, cord):#called when inetracted with fast travel
        if not self.travel_points.get(map, False):#if first time intercted with it
            self.travel_points[map] = cord

class Necklace():        
    def __init__(self, entity):
        self.entity = entity
        self.equipped = {'0':[], '1':[], '2':[]}#equiped omamoris
        self.inventory = {}#omamoris in inventory.: 'Half_dmg':Half_dmg([0,0], entity.game_objects, entity),'Loot_magnet':Loot_magnet([0,0], entity.game_objects, entity),'Boss_HP':Boss_HP([0,0], entity.game_objects, entity)
        entity.dmg_scale = 1#one omamori can make it 0.5 (take half the damage)
        self.level = 1#can be leveld up at black smith

    def level_up(self):#shuold be called from e.g. black smith. bot implement yet
        self.level += 1

    def update(self):
        for omamoris in self.equipped.values():
            for omamori in omamoris:
                omamori.equipped()

    def handle_press_input(self,input):
        for omamoris in self.equipped.values():
            for omamori in omamoris:
                omamori.handle_press_input(input)

    def equip_omamori(self, omamori_string, list_of_places):        
        if self.inventory[omamori_string].state != 'equip':#if not alrady equiped
            number_equipped = len(self.equipped['0']) + len(self.equipped['1']) + len(self.equipped['2'])
            if number_equipped >= 7: return [False, 'no avilable slots']

            new_omamori = getattr(sys.modules[__name__], omamori_string)([0,0], self.entity.game_objects, entity = self.entity)

            if new_omamori.level == 2:
                if self.level == 0: return [False, 'no avilable slots']
                if len(self.equipped['2']) != 0: return [False, 'no avilable slots']

                self.inventory[omamori_string].currentstate.set_animation_name('equip')
                new_omamori.attach()
                new_omamori.set_pos(list_of_places[-1].rect.topleft)
                self.equipped['2'].append(new_omamori)

            elif new_omamori.level == 1:
                if len(self.equipped['1']) + len(self.equipped['2']) >= self.level: return [False, 'no avilable slots']

                self.inventory[omamori_string].currentstate.set_animation_name('equip')
                new_omamori.attach()
                new_omamori.set_pos(list_of_places[7 - self.level + len(self.equipped['1'])].rect.topleft)
                if 7 - self.level + len(self.equipped['1']) == 6:
                    self.equipped['2'].append(new_omamori)
                else:
                    self.equipped['1'].append(new_omamori)

            elif new_omamori.level == 0:
                self.inventory[omamori_string].currentstate.set_animation_name('equip')
                new_omamori.attach()
                new_omamori.set_pos(list_of_places[len(self.equipped['0'])].rect.topleft)
                self.equipped['0'].append(new_omamori)

        else:# If already equipped, remove the omamori
            self.inventory[omamori_string].currentstate.set_animation_name('idle')
            self.inventory[omamori_string].ui_group.empty()

            for key in self.equipped.keys():
                for omamori in self.equipped[key]:
                    if type(omamori).__name__ != omamori_string: continue
                    omamori.detach()
                    self.equipped[key].remove(omamori)
                    break

        return [True]

class Journal():#beast journal 
    def __init__(self):
        self.kills = []

    def update_kill(self,enemy):#called when an enemy is killed
        self.kills.append(enemy)