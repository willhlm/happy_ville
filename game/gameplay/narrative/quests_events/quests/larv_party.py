from gameplay.narrative.quests_events.base import Tasks


class LarvParty(Tasks):#william's larv room
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.number = 20#number of larvs on the map

    def incrase_kill(self):#called when larv_jr is killed: signal
        self.number -= 1
        if self.number <= 0:
            self.complete()

    def initiate_quest(self):
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_ACTIVE)
        self.running = True#a flag to check if the quest is running: needed so that collision only enters here once
        self.game_objects.signals.subscribe('larv_jr_killed', self.incrase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def pause_quest(self):
        self.cleanup()

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):
        self.running = False
        self.game_objects.signals.unsubscribe('larv_jr_killed', self.incrase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

    def complete(self):
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_COMPLETED)
        self.cleanup()
