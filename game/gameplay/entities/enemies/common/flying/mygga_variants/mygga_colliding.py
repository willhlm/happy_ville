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
        self.vitals.set_max_health(3)
        self.vitals.set_health(self.vitals.max_health)
        self.velocity = [random.randint(-2,2),random.randint(-2,2)]
        self.dir[0] = sign(self.velocity[0])
        self.aggro_distance = [0, 0]

    def sway(self, time):#called from walk state
        pass

    def patrol(self, target):
        pass

    def update_vel(self):
        pass

    def handle_platform_collision(self, collision):
        if collision.axis == 'x':
            self.velocity[0] *= -1
            self.dir[0] = -1 if collision.side == 'right' else 1
            return

        self.velocity[1] *= -1
