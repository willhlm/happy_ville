from engine.utils import read_files

class World_state():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        save = read_files.read_json("saves/slots/slot1/save.json")
        self.state = save['world_state']
        self.statistics = save.get('statistics', {'kill': {}, 'amber_droplet': 0, 'death': 0})
        self.progress = save.get('progress', 1)
        self.events = save.get('events', {})
        self.quests = save.get('quests', {})
        self.cutscenes_complete = save.get('cutscenes_complete', {})
        self.defeated_bosses = save.get('defeated_bosses', {})
        self.dialogue = save.get('dialogue', {})

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
        self.state[level_name] = {'loot_container': {}, 'lever': {}, 'gate': {}, 'soul_essence': {}, 'runestone': {}, 'interactable_items': {}, 'breakable_platform': {}, 'bg_fade': {}}#a place holder for things that should depend on map state

    def mark_boss_defeated(self, boss_id):
        """Mark a boss as defeated"""
        self.defeated_bosses[boss_id] = True

    #called from maploader to check if triggers should be loaded
    def is_boss_defeated(self, boss_id):
        """Check if a boss has been defeated"""
        return self.defeated_bosses.get(boss_id, False)
    
    def is_event_complete(self, event_name):
        """Check if an event has occurred"""
        return self.events.get(event_name, False)
    
    def is_cutscene_complete(self, cutscene_name):
        """Check if a cutscene has been played"""
        return self.cutscenes_complete.get(cutscene_name, False)

    # states of obejcts: called from things to check its state
    def _bucket(self, level_name: str, bucket: str) -> dict:
        """Return the dict for e.g. state[level]['gate'] and ensure it exists."""
        self.state[level_name].setdefault(bucket, {})
        return self.state[level_name][bucket]

    def load_bool(self, level_name: str, bucket: str, key, *, initial: bool | None = None) -> bool:
        """
        Load a persisted bool.
        If no saved value exists:
            - `initial` MUST be provided
            - value is persisted
        """

        d = self._bucket(level_name, bucket)

        # Saved value always wins
        if key in d:
            return bool(d[key])        

        d[key] = bool(initial)
        return d[key]

    def set_bool(self, level_name: str, bucket: str, key, value: bool) -> bool:
        d = self._bucket(level_name, bucket)
        d[key] = bool(value)
        return d[key]

    def toggle_bool(self, level_name: str, bucket: str, key) -> bool:
        d = self._bucket(level_name, bucket)
        d[key] = not bool(d[key])
        return d[key]

    def get_dialogue_bucket(self, speaker_id: str) -> dict:
        bucket = self.dialogue.setdefault(speaker_id, {})
        bucket.setdefault('progress', {})
        bucket.setdefault('consumed', {})
        return bucket

    def get_dialogue_progress(self, speaker_id: str, node_id: str) -> int:
        bucket = self.get_dialogue_bucket(speaker_id)
        return int(bucket['progress'].get(node_id, 0))

    def set_dialogue_progress(self, speaker_id: str, node_id: str, progress: int):
        bucket = self.get_dialogue_bucket(speaker_id)
        bucket['progress'][node_id] = int(progress)

    def reset_dialogue_progress(self, speaker_id: str, node_id: str):
        bucket = self.get_dialogue_bucket(speaker_id)
        bucket['progress'].pop(node_id, None)

    def is_dialogue_consumed(self, speaker_id: str, node_id: str) -> bool:
        bucket = self.get_dialogue_bucket(speaker_id)
        return bool(bucket['consumed'].get(node_id, False))

    def consume_dialogue(self, speaker_id: str, node_id: str):
        bucket = self.get_dialogue_bucket(speaker_id)
        bucket['consumed'][node_id] = True
