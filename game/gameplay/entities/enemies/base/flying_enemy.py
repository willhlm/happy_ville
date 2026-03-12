from engine import constants as C
from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.common.flying import states_enemy_flying

class FlyingEnemy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8, C.friction[0]*0.8]

        self.max_vel = [C.max_vel[0], C.max_vel[0]]
        self.dir[1] = 1
        self.currentstate = states_enemy_flying.Patrol(self)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect_y(self):
        self.rect.center = self.hitbox.center
        self.true_pos[1] = self.rect.top

    def update_rect_x(self):
        self.rect.center = self.hitbox.center
        self.true_pos[0] = self.rect.left

    def killed(self):#called when death animation starts playing
        pass

    def limit_y(self):
        pass