from engine.utils import read_files
from gameplay.entities.interactables.chests.base.loot_containers import LootContainers

class Chest_2(Loot_containers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/chest/')
        self.inventory = {'Amber_droplet':1}

    def hit_loot(self):
        pass

