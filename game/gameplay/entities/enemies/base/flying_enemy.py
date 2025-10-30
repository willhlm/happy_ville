import random,  math
from engine import constants as C

from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.common.flying import states_enemy_flying

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class FlyingEnemy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8,C.friction[0]*0.8]

        self.max_vel = [C.max_vel[0],C.max_vel[0]]
        self.dir[1] = 1
        self.currentstate = states_enemy_flying.Patrol(self)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def knock_back(self,amp, dir):
        self.velocity[0] = dir[0]*amp[0]
        self.velocity[1] = -dir[1]*amp[1]

    def chase(self, target_distance):#called from states: when chaising
        self.velocity[0] += (target_distance[0])*0.002 + self.dir[0]*0.1
        self.velocity[1] += (target_distance[1])*0.002 + sign(target_distance[1])*0.1

    def patrol(self, position):#called from states: when patroling
        self.velocity[0] += 0.005*(position[0]-self.rect.centerx)
        self.velocity[1] += 0.005*(position[1]-self.rect.centery)

    def sway(self, time):
        amp = min(abs(self.velocity[0]),0.3)
        self.velocity[1] += amp*math.sin(5*time)# - self.entity.dir[1]*0.1

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