import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files

class PoisonCloud(Projectiles):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = PoisonCloud.sprites
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime=400

    def pool(game_objects):
        PoisonCloud.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/poisoncloud/',game_objects)

    def collision_ene(self,collision_ene):
        pass

    def destroy(self):
        if self.lifetime<0:
            self.currentstate.handle_input('Death')
