from gameplay.narrative.quests_events.base import Tasks
from gameplay.ui.components.overlay.timer import Timer


class LumberjackRadna(Tasks):#called from monument, #TODO need to make so that this radna cannot be eqquiped while this quest is runing
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.description = 'bring back the radna to lumberjack within a given time'
        self.time = 9000#time to compplete
        self.radna = kwarg['item']

    def time_out(self):#called when timer_display runs out
        del self.game_objects.player.backpack.necklace.inventory[self.radna] #remove the radna
        self.game_objects.world_state.narrative.set_quest_status('lumberjack_radna', self.game_objects.world_state.QUEST_FAILED)

    def initiate_quest(self):#called when radna is picked up
        self.game_objects.world_state.narrative.set_quest_status('lumberjack_radna', self.game_objects.world_state.QUEST_ACTIVE)
        self.timer = Timer(self, self.time)
        self.game_objects.cosmetics.add(self.timer)

    def complete(self):#called when talking to lumberjack within the timer limit
        self.timer.kill()
        self.game_objects.world_state.narrative.set_quest_status('lumberjack_radna', self.game_objects.world_state.QUEST_COMPLETED)
