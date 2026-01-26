from engine.utils import read_files

class World_state():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        save = read_files.read_json("saves/slots/slot1/save.json")
        self.state = save['world_state']
        self.statistics = {'kill': {}, 'amber_droplet': 0, 'death': 0}
        self.progress = 1
        self.events = save.get('events', {})  # Load from save
        self.quests = save.get('quests', {})
        self.cutscenes_complete = save.get('cutscenes_complete', {})
        self.defeated_bosses = save.get('defeated_bosses', {}) 

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


    #called from maploader to know if it shold be laoded or not
    def is_boss_defeated(self, boss_id):
        """Check if a boss has been defeated"""
        return self.defeated_bosses.get(boss_id, False)
    
    def mark_boss_defeated(self, boss_id):
        """Mark a boss as defeated"""
        self.defeated_bosses[boss_id] = True
    
    def is_event_complete(self, event_name):
        """Check if an event has occurred"""
        return self.events.get(event_name, False)
    
    def is_cutscene_complete(self, cutscene_name):
        """Check if a cutscene has been played"""
        return self.cutscenes_complete.get(cutscene_name, False)
    
    def check_event(self, event_name):
        """Alias for backwards compatibility"""
        return self.is_event_complete(event_name)