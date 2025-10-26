from engine.utils import read_files
from gameplay.entities.interactables.chests.base.loot_containers import LootContainers

class Chest_3(LootContainers):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.inventory = {'amber_droplet':3}
        self.material = 'metal'

    def hit_loot(self):
        pass

