from gameplay.narrative.quests_events.base import Tasks


class ButterflyEncounter(Tasks):#called from cutscene if aggro path is chosen: and should be called if cocoon gets hurt
    def __init__(self, game_objects):
        super().__init__(game_objects)
        spawn_pos = self.game_objects.map.references['cocoon_boss'].rect.topleft
        self.game_objects.weather.flash()
        butterfly = self.game_objects.registry.fetch('enemies', 'butterfly')(spawn_pos, self.game_objects)
        self.game_objects.enemies.add(butterfly)
        self.game_objects.map.references['cocoon_boss'].currentstate.handle_input('Hurt')
        butterfly.AI.activate()

        self.game_objects.signals.subscribe('butterfly_killed', self.complete)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def complete(self):#called when butterfly is dead
        self.game_objects.world_state.narrative.mark_cutscene_complete(type(self).__name__.lower())
        self.game_objects.world_state.narrative.update_event(type(self).__name__.lower())
        self.cleanup()

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):
        self.game_objects.signals.unsubscribe('butterfly_killed', self.complete)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)
