from .base import EventTrigger


class ButterflyEncounter(EventTrigger):
    blocks_on_event_complete = True

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return
        if not self.game_objects.world_state.statistics_state.statistics['kill'].get('maggot',False): return
        self.game_objects.sequence_manager.start_sequence(self.event)
