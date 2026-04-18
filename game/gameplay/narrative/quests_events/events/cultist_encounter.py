from gameplay.narrative.quests_events.base import Tasks


class CultistEncounter(Tasks):#called from cutscene when meeting the cultist across the bridgr the first time: initiated from cutscene
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.kill = kwarg['kill']
        self.game_objects.signals.subscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.kill -= 1
        if self.kill <= 0:#both cultist have died
            self.complete()

    def handle_player_death(self):# Called when the player dies
        self.cleanup()

    def complete(self):
        self.game_objects.player.death_state.handle_input('idle')
        self.game_objects.world_state.narrative.mark_cutscene_complete(type(self).__name__.lower())
        self.game_objects.world_state.narrative.update_event(type(self).__name__.lower())
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('cultist_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)
