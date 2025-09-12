from gameplay.entities.npc.base.npc import NPC

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_droplet':1}#itam+price
        text = self.dialogue.get_comment()
        self.random_conversation(text)

    def buisness(self):#enters after conversation
        self.game_objects.game.state_manager.enter_state(state_name = 'Vendor', category = 'game_states_facilities', npc = self)

