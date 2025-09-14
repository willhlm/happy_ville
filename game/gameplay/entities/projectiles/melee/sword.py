import pygame, random
from gameplay.entities.projectiles.base.melee import Melee
from engine.utils import read_files

class Sword(Melee):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()
        self.rect = pygame.Rect(entity.rect.centerx,entity.rect.centery,self.image.width*2,self.image.height*2)
        self.hitbox = self.rect.copy()

    def pool(game_objects):
        Sword.sprites = read_files.load_sprites_dict('assets/sprites/attack/sword/', game_objects)

    def init(self):
        self.sprites = Sword.sprites
        self.image = self.sprites['idle'][0]
        self.dmg = self.entity.dmg
        self.lifetime = 10

    def collision_enemy(self, collision_enemy):
        if collision_enemy.flags['invincibility']: return
        collision_enemy.take_dmg(dmg = self.dmg, effects = [lambda: collision_enemy.knock_back(amp = [50, 0], dir = self.dir), lambda: collision_enemy.emit_particles(dir = self.dir)])#TODO insead of lambdas, we could/should maybe change to class based effects
        #slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])#self.entity.cosmetics.add(slash)
        self.clash_particles(collision_enemy.hitbox.center, lifetime = 20, dir = random.randint(-180, 180))

    def clash_particles(self, pos, number_particles = 12, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, **kwarg)
            self.entity.game_objects.cosmetics.add(obj1)
