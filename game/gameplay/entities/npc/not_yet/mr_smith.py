from gameplay.entities.npc.base.npc import NPC

class MrSmith(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Smith', category = 'game_states_facilities', npc = self)

