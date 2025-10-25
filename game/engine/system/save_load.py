from engine.utils import read_files

class Save_load():
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def save_to_file(self):
        save_data = {
            'player': {...},  # you'll need to get player data somehow
            'world_state': self.state,
            'statistics': self.statistics,
            'progress': self.progress,
            'events': self.events,
            'quests': self.quests,
            'cutscenes_complete': self.cutscenes_complete
        }
        read_files.write_json("saves/slots/slot1/save.json", save_data)