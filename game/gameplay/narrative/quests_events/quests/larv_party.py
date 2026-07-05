from gameplay.narrative.quests_events.base import Tasks

class LarvParty(Tasks):#william's larv room
    def __init__(self, game_objects, **kwargs):
        super().__init__(game_objects, **kwargs)
        self.number = int(kwargs.get('kill', 2))#number of larvs on the map
        self.reward = kwargs.get('reward', 'rings')#reward for completing the quest

    def increase_kill(self):#called when larv_jr is killed: signal
        self.number -= 1
        if self.number <= 0:
            self.complete()

    def initiate_quest(self):
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_ACTIVE)
        self.running = True#a flag to check if the quest is running: needed so that collision only enters here once
        self.game_objects.signals.subscribe('larv_jr_killed', self.increase_kill)
        self.game_objects.signals.subscribe('player_died', self.handle_player_death)

    def pause_quest(self):
        self.cleanup()

    def handle_player_death(self):#called when the player dies
        self.cleanup()

    def cleanup(self):
        self.running = False
        self.game_objects.signals.unsubscribe('larv_jr_killed', self.increase_kill)
        self.game_objects.signals.unsubscribe('player_died', self.handle_player_death)

    def _spawn_reward(self):
        reward_cls = self.game_objects.registry.fetch('items', self.reward)
        reward = reward_cls(self.game_objects.player.hitbox.center, self.game_objects)
        self.game_objects.loot.add(reward)

    def complete(self):
        self.game_objects.world_state.narrative.set_quest_status(type(self).__name__.lower(), self.game_objects.world_state.QUEST_COMPLETED)
        self._spawn_reward()
        self.cleanup()
