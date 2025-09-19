import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.visuals.particles import particles

class FlowerButterfly(FlyingEnemy):#peaceful ones
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/flower_butterfly/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/flower_butterfly/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.health = 1
        self.aggro_distance = [0,0]
        self.game_objects.lights.add_light(self, colour = [77/255,168/255,177/255,200/255], interact = False)
        self.flags['aggro'] = False

    def update(self, dt):
        super().update(dt)
        obj1 = particles.FloatyParticles(self.rect.center, self.game_objects, distance = 0, vel = {'linear':[0.1,-1]}, dir = 'isotropic')
        self.game_objects.cosmetics_bg.add(obj1)