from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.interactables import BossRewardBall
from gameplay.entities.shared.boss_rewards import ProgressionUnlockReward

class Boss(Enemy):
    def __init__(self,pos,game_objects, ID = None):
        super().__init__(pos,game_objects)
        self.vitals.set_max_health(10)
        self.vitals.set_health(self.vitals.max_health)
        self.always_active = True
        self.ID = ID
        self.encounter_sequence_key = 'boss_encounter'
        self.reward = None

    def start_aggro(self, delay = 0):
        self.currentstate.clear_tasks()
        if delay and 'wait' in self.currentstate.state_registry:
            self.currentstate.queue_task(task = 'wait', duration = delay)
        self.currentstate.queue_task(task = 'think')
        self.currentstate.start_next_task()

    def start_encounter_sequence(self):
        if not self.ID:
            return
        if self.game_objects.sequence_manager.is_active(self.encounter_sequence_key):
            return
        self.game_objects.sequence_manager.start_sequence(self.encounter_sequence_key, ID=self.ID)

    def dead(self):#called when death animation is finished
        self.flags['aggro'] = False
        self.hit_component.set_invincibility(True) 
        self.game_objects.world_state.narrative.mark_boss_defeated(self.ID)
        if self.ID:
            self.game_objects.signals.emit(self.ID, action="open")

        reward = self.build_reward()
        if reward is not None:
            position = [self.hitbox.centerx, self.hitbox.centery - 50]
            self.game_objects.interactables.add(BossRewardBall(position, self.game_objects, reward))

            self.game_objects.sequence_manager.start_sequence('defeated_boss', boss=self)

    def build_reward(self):
        if self.reward is not None:
            return self.reward

        progress_key = self.game_objects.player.progression.get_progress_key_for_boss(self.ID)
        if progress_key is None:
            return None

        return ProgressionUnlockReward(
            progress_key=progress_key,
            preview_sprite=self.game_objects.player.progression.get_preview_sprite(progress_key),
        )
        
