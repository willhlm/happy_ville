from gameplay.entities.npc.base.npc import NPC

class MsButterfly(NPC):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        self.game_objects.quests_events.initiate_quest('fragile_butterfly')
        self.game_objects.player.inventory['pixie dust'] = 1
