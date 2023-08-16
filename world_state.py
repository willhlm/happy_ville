import Read_files

class World_state():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.cutscenes_complete = []#when a cutscenne has been played, its name gets appended here
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

    def save_travelpoint(self,map,cord):#called when inetracted with savepoint
        try:#if already saved, do nothing
            self.travel_points[map]
        except:#if first time intercted with it
            self.travel_points[map] = cord

    def init_state_file(self,level_name,map_data):#make a state file if it is the first time loading this map
        map_statics = map_data['groups']['bg1']['objects'].get('interactables',False)
        if not map_statics: return#if there are no interactables in this stage

        chest_int = 1
        soul_essence_int = 1

        self.state[level_name] = {'chest':{},'soul_essence':{},'runestone':{}}#a place holder for things that should depend on map state

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

            elif id == 28:#key items: Soul_essence etc.
                for property in obj['properties']:
                    if property['name'] == 'name':
                        keyitem = property['value']

                if keyitem == 'Soul_essence':
                    self.state[level_name]['soul_essence'][str(soul_essence_int)] = 'idle'
                    soul_essence_int += 1

        self.state.pop('placeholder_level', 0)#removes the placeholder tag

class State_tree():#the top node. Should have children that represen main progress events (like killing boss)
    ID = 0#this is will uniqly show which boss that has been killed and in which order
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.parent = None
        self.curr_child = None
        State_tree.ID += 1
        self.ID = State_tree.ID#give unique id when child is made

    def add_child(self, child):
        child.parent = self
        self.children[child.name] = child

    def set_path(self,path):#this should be called when e.g. defeating a boss. Bass the string of boss. It returns the ID of the current state
        if self.curr_child is None:#if there is not child
            self.curr_child = path
            return self.children[path].ID#return the ID
        else:#if there is a child, go down in tree and try again
            return self.children[self.curr_child].set_path(path)

    #for printing
    def print_tree(self):
        spaces = ' ' * self.get_level() * 3
        prefix = spaces + "|__" if self.parent else ""
        print(prefix + self.name, self.ID)
        for child in self.children.keys():
            self.children[child].print_tree()

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

def build_tree():
    main_node = State_tree('Yggdrasill')
    deer = State_tree('Deer')
    main_node.add_child(deer)
    ape = State_tree('Ape')
    main_node.add_child(ape)
    wolf = State_tree('Wolf')
    ai = State_tree('AI')
    deer2 = State_tree('Deer')
    ai.add_child(deer2)
    wolf.add_child(ai)
    main_node.add_child(wolf)
    lion = State_tree('Lion')
    main_node.add_child(lion)

    main_node.print_tree()
    return main_node
