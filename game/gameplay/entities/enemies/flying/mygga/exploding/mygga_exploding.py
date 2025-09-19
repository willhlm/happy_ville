import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from . import states_exploding_mygga

class MyggaExploding(FlyingEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/mygga_exploding/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/exploding_mygga/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 4
        self.attack_distance = [70,70]
        self.aggro_distance = [150,100]
        self.currentstate = states_exploding_mygga.Patrol(self)

    def killed(self):
        self.game_objects.sound.play_sfx(self.sounds['explosion'][0], vol = 0.2)
        self.projectiles.add(Hurt_box(self, size = [64,64], lifetime = 30, dir = [0,0]))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration