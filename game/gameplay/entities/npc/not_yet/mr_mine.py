from gameplay.entities.npc.base.npc import NPC

class MrMine(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = ['reindeer']#priority events to say
        self.event = []#normal events to say
        self.quest = []#quest stuff to say

