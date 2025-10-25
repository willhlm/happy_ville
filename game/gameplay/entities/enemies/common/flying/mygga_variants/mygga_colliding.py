import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files

class MyggaColliding(FlyingEnemy):#bounce around
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/mygga/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3
        self.velocity = [random.randint(-2,2),random.randint(-2,2)]
        self.dir[0] = sign(self.velocity[0])
        self.aggro_distance = [0, 0]

    def sway(self, time):#called from walk state
        pass

    def patrol(self, target):
        pass

    def update_vel(self):
        pass

    #ramp collisions
    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.top = ramp.target
        self.collision_types['top'] = True
        self.velocity[1] *= -1

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.bottom = ramp.target
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1

    #platform collision
    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = -1

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block)
        self.velocity[0] *= -1
        self.dir[0] = 1

    def down_collision(self, block):
        super().down_collision(block)
        self.velocity[1] *= -1

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] *= -1