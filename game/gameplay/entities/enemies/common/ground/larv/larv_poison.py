import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files

class LarvPoison(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv_poison/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.aggro_distance = [180,150]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack_distance = [200,180]

    def attack(self):#called from states, attack main
        attack = Poisonblobb(self.rect.topleft, self.game_objects, dir = self.dir)#make the object
        self.projectiles.add(attack)#add to group but in main phase