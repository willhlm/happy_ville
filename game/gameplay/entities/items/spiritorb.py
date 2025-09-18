import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item import Item

class Spiritorb(Item):#the thing that gives spirit
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/spiritorbs/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def player_collision(self, player):
        player.add_spirit(1)
        self.kill()

    def update_vel(self, dt):
        pass