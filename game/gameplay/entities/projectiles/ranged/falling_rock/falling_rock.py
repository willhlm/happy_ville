import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files
from . import states_droplet

class FallingRock(Projectiles):#things that can be placed in cave, the source makes this and can hurt player
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = FallingRock.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.dmg = 1
        self.currentstate = states_droplet.Idle(self)

    def pool(game_objects):
        FallingRock.sprites = read_files.load_sprites_dict('assets/sprites/animations/falling_rock/rock/', game_objects)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        super().collision_enemy(collision_enemy)
        self.currentstate.handle_input('death')

    def collision_platform(self, collision_plat):#collision platform, called from collusoin_block
        super().collision_platform(collision_plat)
        self.currentstate.handle_input('death')
