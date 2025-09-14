import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import states_crab_crystal

class CrabCrystal(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/crab_crystal/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 16, 16)

        self.currentstate = states_crab_crystal.Idle(self)

        self.hide_distance = [100, 50]#the distance to hide
        self.fly_distance = [150, 50]#the distance to hide
        self.attack_distance = [250, 50]
        self.aggro_distance = [300, 50]

    def chase(self, dir = 1):#called from AI: when chaising
        self.velocity[0] += dir*0.6

    def take_dmg(self,dmg):
        return self.currentstate.take_dmg(dmg)

    def attack(self):#called from currenrstate
        for i in range(0, 3):
            vel = random.randint(-3,3)
            new_projectile = Poisonblobb(self.rect.midtop, self.game_objects, dir = [1, -1], amp = [vel, 4])
            self.game_objects.eprojectiles.add(new_projectile)