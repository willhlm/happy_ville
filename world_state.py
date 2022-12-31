import Read_files

class World_state():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.cutscenes_complete = []#when a cutscenne has been played, its name gets appended here
        self.statistics = {'kill':{},'ambers':0}
        self.progress = 2#overall world progress meter. Increases everytime a boss is killed
        self.state = Read_files.read_json("map_state.json")

    def increase_progress(self):#called when a boss dies
        self.progress += 1

    def update_kill_statistics(self,enemy):#called when an enemy is killed
        try:#have killed it before
            self.statistics['kill'][enemy] += 1#add to kill statisics
        except:#first time killing it
            self.statistics['kill'][enemy] = 1

    def update_money_statistcis(self):#called when amber is picked up
        self.statistics['ambers'] += 1#increaase total money

    def init_state_file(self,level_name,map_data):#make a state file if it is the first time loading this map
        chest_int = 1
        soul_essence_int = 1

        map_statics = map_data['statics']
        self.state[level_name] = {'chest':{},'soul_essence':{},'runestone':{}}#a place holder for things that should depend on map state

        for obj in map_statics:
            id = obj['gid'] - map_data['statics_firstgid']

            if id == 22:#runestone
                for property in obj['properties']:
                    if property['name'] == 'ID':
                        ID = property['value']
                self.state[level_name]['runestone'][ID] = 'idle'

            elif id == 23:#bushes, chests etc
                for property in obj['properties']:
                    if property['name'] == 'type':
                        interactable_type = property['value']

                if interactable_type == 'Chest':
                    self.state[level_name]['chest'][str(chest_int)] = 'idle'
                    chest_int += 1

            elif id == 28:#key items: Soul_essence etc.
                for property in obj['properties']:
                    if property['name'] == 'name':
                        keyitem = property['value']

                if keyitem == 'Soul_essence':
                    self.state[level_name]['soul_essence'][str(soul_essence_int)] = 'idle'
                    soul_essence_int += 1

        self.state.pop('placeholder_level', 0)#removes the placeholder tag

    def save(self):
        pass

    def load(self):
        pass
