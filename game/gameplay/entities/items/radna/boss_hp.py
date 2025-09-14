import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class BossHP(Radna):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = BossHP.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.level = 2
        self.description = 'Visible boss HP ' + '[' + str(self.level) + ']'

    def attach(self):
        for enemy in self.entity.game_objects.enemies.sprites():
            enemy.health_bar()#attached a healthbar on boss

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/radna/boss_HP/',game_objects)#for inventor
        super().pool(game_objects)