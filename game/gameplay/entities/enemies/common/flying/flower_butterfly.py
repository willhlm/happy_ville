import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files

class FlowerButterfly(FlyingEnemy):#peaceful ones
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/flower_butterfly/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/flower_butterfly/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.vitals.set_max_health(1)
        self.vitals.set_health(self.vitals.max_health)
        self.aggro_distance = [0,0]
        self.game_objects.lights.create(self, colour=[77, 168, 177, 200], normal_interact=False)
        self.flags['aggro'] = False

    def update(self, dt):
        super().update(dt)
        self.game_objects.particles.emit('floaty_ambient', self.hitbox.center)
