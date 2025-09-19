import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import states_kusa

class Kusa(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/kusa/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)

        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = [30, 30]
        self.health = 1
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp=2,duration=30)#amplitude and duration