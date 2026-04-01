from engine import constants as C
from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.common.flying import states_enemy_flying
from gameplay.entities.shared.components.body.entity_body import EntityBody

class FlyingEnemy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8, C.friction[0]*0.8]

        self.max_vel = [C.max_vel[0], C.max_vel[0]]
        self.dir[1] = 1
        self.body = EntityBody(self, anchor='center')
        self.currentstate = states_enemy_flying.Patrol(self)

    def on_limit_y(self):
        pass
