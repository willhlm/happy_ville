from gameplay.entities.npc.base.npc import NPC

class MrWood(NPC):#lumber jack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def define_conversations(self):#the elements will pop after saying the stuff
        self.priority = []#priority events to say
        self.event = []#normal events to say
        self.quest = ['lumberjack_radna']#quest stuff to say

    def interact(self):#when plater press t
        self.game_objects.game.state_manager.enter_state(state_name = 'Conversation', npc = self)
        if self.game_objects.world_state.quests.get('lumberjack_radna', False):#if the quest is running
            self.game_objects.quests_events.active_quests['lumberjack_radna'].complete()

    def load_sprites(self):
        super().load_sprites('mr_wood')                