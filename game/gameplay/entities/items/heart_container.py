import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.collision_world_item import CollisionWorldItem

class HeartContainer(CollisionWorldItem):
    item_definition = ItemDefinition(
        item_id='heart_container',
        description='A heart container',
    )
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/heart_container/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def update_vel(self, dt):
        self.velocity[1] = 3*dt

    def pickup(self, player):
        player.vitals.set_max_health(player.vitals.max_health + 1)
        #a cutscene?
        self.kill()
