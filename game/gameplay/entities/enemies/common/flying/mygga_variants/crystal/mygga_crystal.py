import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from . import states_mygga_crystal

class MyggaCrystal(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/mygga_crystal/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 3

        self.currentstate = states_mygga_crystal.Patrol(self)

        self.flee_distance = [50, 50]#starting fleeing if too close
        self.attack_distance = [100, 100]#attack distance
        self.aggro_distance = [150, 100]#start chasing

    def attack(self):#called from state
        dirs = [[1,1], [-1,1], [1,-1], [-1,-1]]
        for direction in dirs:
            obj = Poisonblobb(self.hitbox.topleft, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)

    def chase(self, direction):#called from state: when chaising
        self.velocity[0] += direction[0]*0.5
        self.velocity[1] += direction[1]*0.5

    def patrol(self, position):#called from state: when patroling
        self.velocity[0] += (position[0]-self.rect.centerx) * 0.002
        self.velocity[1] += (position[1]-self.rect.centery) * 0.002