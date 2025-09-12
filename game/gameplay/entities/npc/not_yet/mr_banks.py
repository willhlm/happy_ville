from gameplay.entities.npc.base.npc import NPC

class MrBanks(NPC):#bank
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.ammount = 0

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Bank', category = 'game_states_facilities', npc = self)

