from gameplay.entities.npc.base.npc import NPC

class MrCarpenter(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def load_sprites(self):
        super().load_sprites('mr_carpenter')    
