import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files

class Egg(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('assets/sprites/enentitiesteties/enemies/egg/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.number = random.randint(1, 4)
        self.aggro_distance = -1 #if negative, it will not go into aggro

    def knock_back(self,dir):
        pass

    def death(self):
        self.spawn_minions()
        self.kill()

    def spawn_minions(self):
        pos = [self.hitbox.centerx,self.hitbox.centery-10]
        for i in range(0,self.number):
            obj = Slime(pos,self.game_objects)
            obj.velocity=[random.randint(-100, 100),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)