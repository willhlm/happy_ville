from gameplay.narrative.quests_events.base import Tasks


class MiniBoss(Tasks):
    def __init__(self, game_objects, **kwargs):
        super().__init__(game_objects)
        self.game_objects.signals.emit('miniboss')#the e.g. gates to trigger
        self.boss_id = kwargs['boss_id']
        self.game_objects.signals.subscribe('miniboss_defeat', self.complete) #should be called when the miniboss is defeated

    def complete(self):
        self.game_objects.world_state.narrative.mark_boss_defeated(self.boss_id)
        self.game_objects.world_state.narrative.update_event('mini_boss')
        self.game_objects.signals.unsubscribe('miniboss_defeat', self.complete)
