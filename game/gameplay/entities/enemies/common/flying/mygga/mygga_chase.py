import pygame, math
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files

def sign(number):
    if number == 0: return 0
    elif number > 0: return 1
    else: return -1

class MyggaChase(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.aggro_distance = [130, 80]
        self.accel = [0.013, 0.008]
        self.accel_chase = [0.026, 0.009]
        self.deaccel_knock = 0.84
        self.max_chase_vel = 1.8
        self.max_patrol_vel = 1.2
        self.friction = [0.009,0.009]

    def knock_back(self, amp, dir):
        self.currentstate.enter_state('Knock_back')
        amp = 19
        if dir[1] != 0:
            self.velocity[1] = -dir[1] * amp
        else:
            self.velocity[0] = dir[0] * amp

    def player_collision(self, player):#when player collides with enemy
        super().player_collision(player)
        self.velocity = [0, 0]
        self.currentstate.enter_state('Wait', time = 30, next_AI = 'Chase')

    def patrol(self, position):#called from state: when patroling
        self.velocity[0] += sign(position[0] - self.rect.centerx) * self.accel[0]
        self.velocity[1] += sign(position[1] - self.rect.centery) * self.accel[1]
        self.velocity[0] = min(self.max_chase_vel, self.velocity[0])
        self.velocity[1] = min(self.max_chase_vel, self.velocity[1])

    def chase(self, target_distance):#called from state: when chaising
        self.velocity[0] += sign(target_distance[0]) * self.accel_chase[0]
        self.velocity[1] += sign(target_distance[1]) * self.accel_chase[1]
        for i in range(2):
            if abs(self.velocity[i]) > self.max_chase_vel:
                self.velocity[i] = sign(self.velocity[i]) *  self.max_chase_vel

    def chase_knock_back(self, target_distance):#called from state: when chaising
        self.velocity[0] *= self.deaccel_knock#sign(target_distance[0])
        self.velocity[1] *= self.deaccel_knock#sign(target_distance[1])

    def sway(self, time):#called from walk state
        amp = min(abs(self.velocity[0]),0.008)
        self.velocity[1] += amp*math.sin(2.2*time)# - self.entity.dir[1]*0.1