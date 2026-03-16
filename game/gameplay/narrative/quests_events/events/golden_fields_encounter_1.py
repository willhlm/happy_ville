import random

from gameplay.entities.enemies import CultistRogue
from gameplay.narrative.quests_events.base import Tasks


class GoldenFieldsEncounter1(Tasks):#called from golden fields room event_trigger
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.get_gates()
        self.spawn_enemy()
        self.game_objects.signals.subscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def spawn_enemy(self):
        self.number = 1
        for number in range(0, self.number):
            pos = [1728 +  random.randint(-10, 10), 1200 +  random.randint(-10, 10)]
            enemy = CultistRogue(pos, self.game_objects)
            self.game_objects.enemies.add(enemy)

    def get_gates(self):#trap aila
        self.gates = {}
        for gate in self.game_objects.map.references['gate']:
            if gate.ID_key == 'golden_fields_encounter_1_1':#these strings are specified in tiled
                self.gates['1'] = gate
                self.gates['1'].currentstate.handle_input('Transform')
            elif gate.ID_key == 'golden_fields_encounter_1_2':#these strings are specified in tiled
                self.gates['2'] = gate#this one is already erect

    def handle_player_death(self):# Called when the player dies
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

    def incrase_kill(self):#called when enemy is called
        self.number -= 1
        if self.number == 0:#all enemies eleminated
            self.complete()

    def complete(self):
        for key in self.gates.keys():
            self.gates[key].currentstate.handle_input('Transform')
        self.game_objects.world_state.narrative.update_event(type(self).__name__.lower())
        self.cleanup()
