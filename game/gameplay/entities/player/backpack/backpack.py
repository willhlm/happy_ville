from gameplay.entities.player.backpack.inventory import Inventory
from gameplay.entities.player.backpack.map_state import MapState
from gameplay.entities.player.backpack.radna_loadout import RadnaLoadout
from gameplay.entities.player.backpack.journal import Journal


class Backpack():#Ailas back pack. Can append new things such as journal, if picked up
    def __init__(self, entity):
        self.holdings = {'map': MapState(), 'inventory': Inventory(entity.game_objects), 'radna': RadnaLoadout()}
        self._registery = {'journal': Journal}

    @property
    def inventory(self):
        return self.holdings['inventory']

    @property
    def map(self):
        return self.holdings['map']

    @property
    def radna(self):
        return self.holdings['radna']        

    @property
    def journal(self):
        return self.holdings['journal']    

    def add_holding(self, name):
        self.holdings[name] = self._registery[name]()