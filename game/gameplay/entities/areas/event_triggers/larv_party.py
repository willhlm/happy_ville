from .base import EventTrigger


class StartLarvParty(EventTrigger):
    blocks_on_event_complete = False

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return
        if self.game_objects.world_state.narrative.is_quest_completed('larv_party'): return
        if self.game_objects.quests_events.active_quests.get('larv_party', False):
            if self.game_objects.quests_events.active_quests['larv_party'].running: return
            self.game_objects.quests_events.active_quests['larv_party'].initiate_quest()
        else:
            self.game_objects.quests_events.initiate_quest('larv_party', **self.kwarg)


class StopLarvParty(EventTrigger):
    blocks_on_event_complete = False

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return
        if not self.game_objects.quests_events.active_quests.get('larv_party', False): return
        if not self.game_objects.quests_events.active_quests['larv_party'].running: return
        self.game_objects.quests_events.active_quests['larv_party'].pause_quest()
