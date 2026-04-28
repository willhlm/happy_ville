import pygame
from engine.utils import read_files
from gameplay.entities.items.base.collision_world_item import CollisionWorldItem
from gameplay.entities.items.base.item_definition import ItemDefinition
#from gameplay.entities.visuals.particles import particles

class SoulEssence(CollisionWorldItem):#genkidama
    item_definition = ItemDefinition(
        item_id='soul_essence',
        description='An essence container',
    )
    def __init__(self, pos, game_objects, ID_key = None):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/soul_essence/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox=self.rect.copy()
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def pickup(self, player):
        player.backpack.inventory.add_item(self.get_item_id())
        self.game_objects.world_state.objects.set_bool(self.game_objects.map.biome_room_name, 'soul_essence', self.ID_key, True)#write in the state file that this has been picked up
        #make a cutscene?TODO
        self.kill()

    def update(self, dt):
        super().update(dt)
        self.game_objects.particles.emit('spark_scatter',self.rect.center, colour = [255,255,255,255] )
        #obj1 = getattr(particles, 'Spark')(self.rect.center, self.game_objects, distance = 100, lifetime=20, vel={'linear':[2,4]}, fade_scale = 10)
        #self.game_objects.cosmetics.add(obj1)

    def update_vel(self, dt):
        pass
