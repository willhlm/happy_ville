from gameplay.entities.npc.base.npc import NPC

class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        if self.game_objects.world_state.state.get('reindeer', False):#if player has deafated the reindeer
            if not self.game_objects.player.states['Wall_glide']:#if player doesn't have wall yet (so it only enters once)
                self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game.game_objects.player.sprites[Wall_glide][0].copy())
                self.game_objects.player.states['Wall_glide'] = True

    def load_sprites(self):
        super().load_sprites('aslat')