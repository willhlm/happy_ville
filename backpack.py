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
        self.items = {}#{"healthpotion": {"item": <Item instance>, "quantity": 3}}

    def get_item(self, item_name):
        if item_name in self.items:
            return self.items[item_name]['item']
        return False

    def add(self, item, quantity=1):
        name = type(item).__name__.lower()
        if self.items.get(name, False):
            self.items[name]["quantity"] += quantity
        else:#new item
            new_item = type(item)([0,0], item.game_objects)#make a copy
            new_item.set_ui()
            self.items[name] = {"item": new_item, "quantity": quantity}            

    def remove(self, item_name, quantity=1):
        self.items[item_name]["quantity"] -= quantity
    
    def get_quantity(self, item_name):#return quantity. If item doesn't exist, return 0
        return self.items.get(item_name, {}).get("quantity", 0)

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
        self.equipped = {}#rings with radna {'fingers': <Ring instance>}
        self.inventory = {}#radnas in inventory: # {"half_dmg":  <Half_dmg instance>}
        self._available_slots = ['index', 'long', 'ring', 'small']
        self.rings = {}#rings in inventory: {'fingers': <Ring instance>}

    def get_radna(self, item_name):
        return self.inventory.get(item_name, False)

    def get_ring(self, item_name):
        return self.rings.get(item_name, False)

    def add(self, item):
        name = type(item).__name__.lower()
        item.set_ui()
        self.inventory[name] = item

    def add_ring(self, ring):#strong the objects
        for slot in self._available_slots:
            if slot not in self.rings:                
                self.rings[slot] = ring
                ring.set_finger(slot)
                break

    def update(self):
        for ring in self.equipped.values():
            ring.update_equipped()

    def handle_press_input(self, input):
        for ring in self.equipped.values():
            ring.handle_press_input(input)

    def check_position(self, radna):
        for slot in self.rings.keys():
            ring = self.rings[slot]            
            if ring.level < radna.level: continue#if not enough level
            if self.equipped.get(slot, False): continue#if the slot if occupied
            return slot 

    def equip_item(self, radna): #called from backpack, to add a radna on to a ring
        for slot in self.rings.keys():#attach a radna objet to a ring
            ring = self.rings[slot]            
            if ring.level < radna.level: continue#if not enough level
            if self.equipped.get(slot, False): continue#if the slot if occupied
            ring.attach_radna(radna)    
            self.equipped[slot] = ring
            break

    def remove_item(self, radna): #called from backpack, to remove a radna from a ring
        for slot in self.rings.keys():#attach a radna objet to a ring
            ring = self.rings[slot]
            if ring.radna == radna:
                ring.detach_radna(radna)    
                del self.equipped[slot]    
                break  

class Journal():#beast journal 
    def __init__(self):
        self.kills = []

    def update_kill(self,enemy):#called when an enemy is killed
        self.kills.append(enemy)