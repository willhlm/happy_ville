import pygame 
from engine.utils import read_files
from gameplay.entities.enemies.base.enemy import Enemy
from config.enemies import ENEMY_CONFIGS

class LarvJr(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIGS['rav']

        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv_jr/', game_objects, True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],22,12)
        self.attack_distance = [0,0]
        self.init_x = self.rect.x

        self.patrol_speed = self.config['speeds']['patrol']
        self.patrol_timer = self.config['timers']['patrol']

        self.health = 3
        self.currentstate.enter_state('Patrol')

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('larv_jr_killed')#emit this signal

    def walk(self):
        self.velocity[0] += self.dir[0]*0.22        