import pygame, math
from engine.utils import read_files
from gameplay.entities.items.base.item import Item

class MemoryShard(Item):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/memory_shard/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

        self.time = 0

    def update_vel(self, dt):
        self.time += dt * 0.1
        self.velocity[1] = 0.5 * math.cos(self.time)

    def on_collision(self, entity):
        pass