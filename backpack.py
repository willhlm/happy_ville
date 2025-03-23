class Backpack():#Ailas back pack. Can append new things such as journal, if picked up
    def __init__(self, entity):
        self.holdings = {'map': Map(), 'inventory': Inventory(), 'necklace': Necklace(entity), 'journal': Journal()}
        
class Inventory():          
    def __init__(self):
        self.items = {'amber_droplet': 403, 'bone': 2, 'soul_essence': 10, 'tungsten': 10}#the keys need to have the same name as their respective classes

    def add(self, item):#called everytime an item is picked up
        self.items.setdefault(item, 0)
        self.items[item] += 1

class Map():        
    def __init__(self):
        self.spawn_point = {'map': 'light_forest_1', 'point': '1', 'safe_spawn' : [0,0]}#can append bone
        self.travel_points = {}#Fast travel system will read this dict. The key is the map, value is the coordinate. Appends the info when the travel is unlocked
        self.visited_bioms = {}#should 

    def new_biome(self, biome):#called when a new biome is visited
        self.visited_bioms[biome] = True

    def savepoint(self, map, point):#called when interact with savepoint
        self.spawn_point['map'] = map
        self.spawn_point['point'] = point

    def safe_spawn(self, coordinate):#called wheb collliding with safe spawn
        self.spawn_point['safe_spawn'] = coordinate

    def append_bone(self):#called when plaiting a bone
        pass

    def save_travelpoint(self, map, cord):#called when inetracted with fast travel
        if not self.travel_points.get(map, False):#if first time intercted with it
            self.travel_points[map] = cord

class Necklace():        
    def __init__(self, entity):
        self.entity = entity
        self.equipped = {'0':[],'1':[],'2':[]}#equiped omamoris
        self.inventory = {}#omamoris in inventory.: 'Half_dmg':Half_dmg([0,0], entity.game_objects, entity),'Loot_magnet':Loot_magnet([0,0], entity.game_objects, entity),'Boss_HP':Boss_HP([0,0], entity.game_objects, entity)
        entity.dmg_scale = 1#one omamori can make it 0.5 (take half the damage)
        self.level = 1#can be leveld up at black smith

    def level_up(self):#shuold be called from black smith. bot implement yet
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