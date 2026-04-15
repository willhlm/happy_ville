class MapState:
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
        self.spawn_point['bone'] = {'map': map, 'point': point}

    def save_travelpoint(self, map, cord):#called when inetracted with fast travel
        if not self.travel_points.get(map, False):#if first time intercted with it
            self.travel_points[map] = cord
