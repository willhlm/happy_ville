from engine.utils import read_files

class Save_load():
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def save_to_file(self):
        world_state = self.game_objects.world_state
        save_data = {
            'player': {...},  # you'll need to get player data somehow
            'world_state': world_state.state,
            'statistics': world_state.statistics,
            'progress': world_state.progress,
            'events': world_state.events,
            'quests': world_state.quests,
            'cutscenes_complete': world_state.cutscenes_complete,
            'defeated_bosses': world_state.defeated_bosses,
            'dialogue': world_state.dialogue,
        }
        read_files.write_json("saves/slots/slot1/save.json", save_data)
