import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.world_item import WorldItem
from gameplay.entities.items.base.components import CollisionPickupComponent

class SpiritContainer(WorldItem):
    item_definition = ItemDefinition(
        description='A spirit container',
    )
    pickup_component_cls = CollisionPickupComponent

    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/spirit_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def update_vel(self, dt):
        self.velocity[1]=3*dt

    def pickup(self, player):
        player.vitals.set_max_spirit(player.vitals.max_spirit + 1)
        #a cutscene?
        self.kill()
