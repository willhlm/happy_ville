import Read_files

class World_state():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.cutscenes_complete = {}#when a cutscenne has been played, its name gets appended here
        self.statistics = {'kill':{},'ambers':0}#collects stuff aila has done
        self.state = Read_files.read_json("map_state.json")
        self.travel_points = {}#Fast travel system will read this dict. The key is the map, value is the coordinate. Appends the info when the travel is unlocked
        self.define_events()
        self.progress = 1#should tick everytime an event occures which modifies the happinies (e.g. a boss dies)

    def define_events(self):#all events that should have a flag
        self.events = {'reindeer':False,'aslat':False,'ape':False}

    def update_event(self,event):#called when an event has happened and set it to True
        self.events[event] = True

    def increase_progress(self):#called when e.g. a boss dies. It is the happinies degree of the world
        self.progress += 1

    def update_kill_statistics(self,enemy):#called when an enemy is killed
        try:#have killed it before
            self.statistics['kill'][enemy] += 1#add to kill statisics
        except:#first time killing it
            self.statistics['kill'][enemy] = 1

    def update_money_statistcis(self):#called when amber is picked up
        self.statistics['ambers'] += 1#increaase total money

    def save_travelpoint(self,map,cord):#called when inetracted with fast travel
        try:#if already saved, do nothing
            self.travel_points[map]
        except:#if first time intercted with it
            self.travel_points[map] = cord

    def init_state_file(self,level_name,map_data):#make a state file if it is the first time loading this map
        map_statics = map_data['groups']['bg1']['objects'].get('interactables',False)#check if we have interactaböes in thi smap
        if not map_statics: return#if there are no interactables in this stage

        chest_int = 1
        soul_essence_int = 1

        self.state[level_name] = {'chest':{},'lever':{},'soul_essence':{},'runestone':{}}#a place holder for things that should depend on map state

        for obj in map_statics['objects']:
            id = obj['gid'] - map_data['interactables_firstgid']

            if id == 3:#runestone
                for property in obj['properties']:
                    if property['name'] == 'ID':
                        ID = property['value']
                self.state[level_name]['runestone'][ID] = 'idle'

            elif id == 4:#chests
                self.state[level_name]['chest'][str(chest_int)] = 'idle'
                chest_int += 1

            elif id == 10:#lever
                for property in obj['properties']:
                    if property['name'] == 'ID':
                        ID = property['value']
                self.state[level_name]['lever'][ID] = 'idle'

            elif id == 28:#key items: Soul_essence etc.
                for property in obj['properties']:
                    if property['name'] == 'name':
                        keyitem = property['value']

                if keyitem == 'Soul_essence':
                    self.state[level_name]['soul_essence'][str(soul_essence_int)] = 'idle'
                    soul_essence_int += 1

        self.state.pop('placeholder_level', 0)#removes the placeholder tag
