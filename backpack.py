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
        self.items = {}# { "healthpotion": 3, "amber": 1 }

    def add(self, item_name, quantity = 1):  # Allow adding multiple at once
        self.items.setdefault(item_name, 0)
        self.items[item_name] += quantity

    def remove(self, item_name, quantity = 1):
        self.items[item_name] -= quantity
    
    def get_quantity(self, item_name):#return quantity. If item doesn't exist, return 0
        return self.items.get(item_name, 0)

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
        self.equipped = {}#equiped rings
        self.inventory = {'half_dmg': 1}#radnas in inventory

    def add(self, item_name):  # Allow adding multiple at once
        self.inventory.setdefault(item_name, 0)
        self.inventory[item_name] += 1

    def remove(self, item_name):
        self.inventory[item_name] -= 1

    def update(self):
        for ring in self.equipped.values():
            ring.update()

    def handle_press_input(self,input):
        for ring in self.equipped.values():
            ring.handle_press_input(input)

    def equip_item(self, item_name):        
        pass

class Journal():#beast journal 
    def __init__(self):
        self.kills = []

    def update_kill(self,enemy):#called when an enemy is killed
        self.kills.append(enemy)