import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.components import ItemLifetimeComponent
from gameplay.entities.items.base.collision_world_item import CollisionWorldItem

class Bone(CollisionWorldItem):
    item_definition = ItemDefinition(
        item_id='bone',
        description='Ribs from my daugther. You can respawn and stuff',
    )
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.lifetime_component = ItemLifetimeComponent(self, lifetime=500)
        self.sprites = Bone.sprites
        self.sounds = Bone.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1],16,16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)

    def pickup(self, player):
        self.add_to_inventory(player)

    @staticmethod
    def use_from_inventory(record):
        inventory = record.game_objects.player.backpack.inventory
        if inventory.get_quantity(record.item_id) <= 0:
            return False

        inventory.remove(record.item_id)
        record.game_objects.player.backpack.map.save_bone(
            map=record.game_objects.map.biome_room_name,
            point=record.game_objects.camera_manager.camera.scroll,
        )
        record.game_objects.player.currentstate.enter_state('Plant_bone_main')
        return True

    def pool(game_objects):#all things that should be saved in object pool
        Bone.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/bone/',game_objects)
        Bone.sounds = read_files.load_sounds_dict('assets/audio/sfx/audio/sfx/entities/items/bone/')

    def release_texture(self):#stuff that have pool shuold call this
        pass
