from engine.utils import read_files
from gameplay.entities.interactables.chests.base.loot_containers import LootContainers

class AmberRock(LootContainers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/interactables/amber_rock/')
        self.inventory = {'Amber_droplet':3}