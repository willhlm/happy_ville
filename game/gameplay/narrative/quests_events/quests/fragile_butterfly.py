from gameplay.narrative.quests_events.base import Tasks


class FragileButterfly(Tasks):#light forest cave
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.description = 'could you deliver my pixie dust to my love. Do not take damage.'

    def fail(self):#should be called when taking dmg
        self.game_objects.world_state.narrative.set_quest_status('fragile_butterfly', self.game_objects.world_state.QUEST_FAILED)

    def initiate_quest(self):#called to initiate
        self.game_objects.world_state.narrative.set_quest_status('fragile_butterfly', self.game_objects.world_state.QUEST_ACTIVE)

    def complete(self):#called when delivered
        self.game_objects.world_state.narrative.set_quest_status('fragile_butterfly', self.game_objects.world_state.QUEST_COMPLETED)
