from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.bosses.shared.defeated_boss import DefeatedBoss
from gameplay.entities.interactables import AbilityBall

class Boss(Enemy):
    def __init__(self,pos,game_objects, ID = None):
        super().__init__(pos,game_objects)
        self.health = 10
        self.always_active = True
        self.ID = ID

    def start_aggro(self, delay = 0):
        self.currentstate.clear_tasks()
        if delay and 'wait' in self.currentstate.state_registry:
            self.currentstate.queue_task(task = 'wait', duration = delay)
        self.currentstate.queue_task(task = 'think')
        self.currentstate.start_next_task()

    def dead(self):#called when death animation is finished
        self.hit_component.set_invinsibility(True) 
        self.game_objects.world_state.narrative.mark_boss_defeated(self.ID)
        
        position = [self.hitbox.centerx, self.hitbox.centery - 50]
        self.game_objects.interactables.add(AbilityBall(position, self.game_objects, self.ability))

        self.game_objects.cosmetics.add(DefeatedBoss(self.game_objects, self))
        
