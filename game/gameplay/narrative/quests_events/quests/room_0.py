import random

from gameplay.entities.enemies import CultistRogue
from gameplay.narrative.quests_events.quests.portal_rooms import PortalRooms


class Room0(PortalRooms):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)

    def initiate_room(self):#specific for each room
        self.put_gate()
        self.number = 1
        for number in range(0, self.number):
            pos = [600 +  random.randint(-100, 100), 300 +  random.randint(-100, 100)]
            enemy = CultistRogue(pos, self.game_objects)
            self.game_objects.enemies.add(enemy)

        self.game_objects.signals.subscribe('cultist_killed', self.incrase_kill)

    def cleanup(self):
        super().cleanup()
        self.game_objects.signals.unsubscribe('cultist_killed', self.incrase_kill)
