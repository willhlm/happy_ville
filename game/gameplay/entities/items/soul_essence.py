import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item import Item
from gameplay.entities.visuals.particles import particles

class SoulEssence(Item):#genkidama
    def __init__(self, pos, game_objects, ID_key = None):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/soul_essence/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox=self.rect.copy()
        self.description = 'An essence container'#for shops
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def player_collision(self, player):
        player.backpack.inventory.add(self)
        self.game_objects.world_state.state[self.game_objects.map.level_name]['soul_essence'][self.ID_key] = True#write in the state file that this has been picked up
        #make a cutscene?TODO
        self.kill()

    def update(self, dt):
        super().update(dt)
        obj1 = getattr(particles, 'Spark')(self.rect.center, self.game_objects, distance = 100, lifetime=20, vel={'linear':[2,4]}, fade_scale = 10)
        self.game_objects.cosmetics.add(obj1)

    def update_vel(self, dt):
        pass