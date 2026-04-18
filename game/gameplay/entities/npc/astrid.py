from gameplay.entities.npc.base.npc import NPC

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_droplet':1}#itam+price

    def on_conversation_complete(self):
        self.game_objects.game.state_manager.enter_state(state_name = 'Vendor', category = 'game_states_facilities', npc = self)

    def load_sprites(self):
        super().load_sprites('astrid')
