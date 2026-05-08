import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.collision_world_item import CollisionWorldItem

class Spiritorb(CollisionWorldItem):#the thing that gives spirit
    item_definition = ItemDefinition(
        item_id='spiritorb',
        description='A spirit orb',
    )
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/spiritorbs/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def pickup(self, player):
        player.gain_spirit(1)
        self.kill()

    def update_vel(self, dt):
        pass
