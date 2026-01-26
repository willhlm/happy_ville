from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.bosses.shared.defeated_boss import DefeatedBoss
from gameplay.entities.interactables import AbilityBall

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 10        

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        position = [self.hitbox.centerx, self.hitbox.centery - 50]
        self.game_objects.interactables.add(AbilityBall(position, self.game_objects, self.ability))

        self.game_objects.cosmetics.add(DefeatedBoss(self.game_objects, self))

