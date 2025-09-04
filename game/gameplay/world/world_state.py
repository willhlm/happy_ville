from engine.utils import read_files

class World_state():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.state = read_files.read_json("saves/map_state/map_state.json")#save the state of each map (i.e. if chest has been opened, soul essence picoed up etc)
        self.statistics = {'kill': {}, 'amber_droplet' : 0, 'death': 0}#collects stuff aila has done, number of deaths
        self.progress = 1#should tick everytime an event occures which modifies the happinies (e.g. a boss dies)
        self.events = {}#save events and put it to True when completed -> events, such as boss defeat
        self.quests = {}#true means completed, false means still active -> tasks
        self.cutscenes_complete = {}#when a cutscenne has been played, its name gets appended here

    def cutscene_complete(self, event):
        self.cutscenes_complete[event] = True

    def update_event(self, event):
        self.events[event] = True

    def increase_progress(self):#called when e.g. a boss dies. It is the happinies degree of the world
        self.progress += 1

    def update_kill_statistics(self,enemy):#called when an enemy is killed
        self.statistics['kill'].setdefault(enemy, 0)
        self.statistics['kill'][enemy] += 1            

    def update_statistcis(self, key):#called when amber is picked up
        self.statistics[key] += 1#increaase total money, deaths etc

    def init_state_file(self, level_name):#make a state file if it is the first time loading this map, state of different interactables
        self.state[level_name] = {'loot_container': {}, 'lever': {}, 'soul_essence': {}, 'runestone': {}, 'interactable_items': {}, 'breakable_platform': {}, 'bg_fade': {}}#a place holder for things that should depend on map state
        self.state.pop('placeholder_level', 0)#removes the placeholder tag
