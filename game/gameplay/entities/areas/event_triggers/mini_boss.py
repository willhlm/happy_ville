from .base import EventTrigger


class MiniBoss(EventTrigger):
    blocks_on_event_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.boss_id = f"{game_objects.map.biome_room_name}_{int(pos[0])}_{int(pos[1])}"

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return
        if self.game_objects.world_state.narrative.is_boss_defeated(self.boss_id): return
        self.game_objects.quests_events.initiate_event('mini_boss', boss_id = self.boss_id)
        self.kill()
