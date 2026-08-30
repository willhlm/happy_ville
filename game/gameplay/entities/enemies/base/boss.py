from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.interactables import BossRewardBall
from gameplay.entities.shared.boss_rewards import ProgressionUnlockReward

class Boss(Enemy):
    reward_progress_key = None
    def __init__(self,pos,game_objects, ID = None):
        super().__init__(pos,game_objects)
        self.vitals.set_max_health(10)
        self.vitals.set_health(self.vitals.max_health)
        self.always_active = True
        self.ID = ID
        self.encounter_sequence_key = 'boss_encounter'
        self.reward = None
        self.reward_spawn_position = None

    def start_aggro(self, delay = 0):
        self.currentstate.clear_tasks()
        if delay and 'wait' in self.currentstate.state_registry:
            self.currentstate.queue_task(task = 'wait', duration = delay)
        self.currentstate.queue_task(task = 'think')
        self.currentstate.start_next_task()

    def run_tasks(self, tasks, start=True, clear=True):
        if clear:
            self.currentstate.clear_tasks()
        for task in tasks:
            self.currentstate.queue_task(**task)
        if start:
            self.currentstate.start_next_task()

    def start_encounter_sequence(self):
        if not self.ID:
            return
        if self.game_objects.sequence_manager.is_active(self.encounter_sequence_key):
            return
        self.game_objects.sequence_manager.start_sequence(self.encounter_sequence_key, encounter=self.ID)

    def dead(self):#called when death animation is finished
        self.flags['aggro'] = False
        self.hit_component.set_invincibility(True) 
        self.game_objects.world_state.narrative.mark_boss_defeated(self.ID)
        self.game_objects.world_controller.refresh_all()
        if self.ID:
            self.game_objects.signals.emit(self.ID, action="open")

        reward = self.build_reward()
        if reward is not None:
            position = self.reward_spawn_position or [self.hitbox.centerx, self.hitbox.centery - 50]
            self.game_objects.world_state.narrative.set_boss_reward_position(self.ID, position)
            self.game_objects.interactables.add(BossRewardBall(position, self.game_objects, reward, self.ID))

            self.game_objects.sequence_manager.start_sequence('defeated_boss', boss=self)

    def build_reward(self):
        if self.reward is not None:
            return self.reward

        return self.build_reward_for_boss(self.game_objects, self.ID)

    @classmethod
    def build_reward_for_boss(cls, game_objects, boss_id):
        progress_key = game_objects.player.progression.get_progress_key_for_boss(boss_id)
        if progress_key is None:
            progress_key = cls.reward_progress_key
        if progress_key is None:
            return None

        return ProgressionUnlockReward(
            progress_key=progress_key,
        )
        
