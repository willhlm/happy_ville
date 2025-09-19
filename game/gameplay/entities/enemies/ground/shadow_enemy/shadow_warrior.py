import pygame 
from engine.utils import read_files
from gameplay.entities.enemies.base.shadow_enemy import ShadowEnemy

class ShadowWarrior(ShadowEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/cultist_warrior/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 3
        self.attack_distance = [80,10]

    def update(self, dt):
        super().update(dt)
        self.check_light()

    def attack(self):#called from states, attack main
        self.projectiles.add(Sword(self))#add to group