import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files

class SlamAttack(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = SlamAttack.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate.enter_state('Death')
        self.animation.play('idle')
        self.dir = kwarg.get('dir', [1, 0])
        self.dmg = 1

    def pool(game_objects):
        SlamAttack.sprites = read_files.load_sprites_dict('assets/sprites/attack/slam/', game_objects, flip_x = True)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        collision_enemy.take_dmg(dmg = self.dmg, effects = [lambda: collision_enemy.knock_back(amp = [50, 0], dir = self.dir)])

    def collision_platform(self, collision_plat):#collision platform
        pass

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        eprojectile.take_dmg(self.dmg)
