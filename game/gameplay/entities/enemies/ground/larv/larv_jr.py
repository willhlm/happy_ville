import pygame 
from engine.utils import read_files
from gameplay.entities.enemies.base.enemy import Enemy

class LarvJr(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/larv_jr/', game_objects, True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],22,12)
        self.attack_distance = [0,0]
        self.init_x = self.rect.x
        self.patrol_dist = 100
        self.health = 3

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('larv_jr_killed')#emit this signal

    def walk(self):
        self.velocity[0] += self.dir[0]*0.22        