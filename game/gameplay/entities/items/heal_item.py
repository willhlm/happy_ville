import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.components import ItemLifetimeComponent, CollisionPickupComponent
from gameplay.entities.items.base.world_item import WorldItem

class HealItem(WorldItem):
    item_definition = ItemDefinition(
        description='Use it to heal',
    )
    pickup_component_cls = CollisionPickupComponent

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.lifetime_component = ItemLifetimeComponent(self, lifetime=500)
        self.sprites = HealItem.sprites
        self.sounds = HealItem.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1],16,16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)

    def pickup(self, player):
        self.pickup_component.collect_to_inventory(self, player)

    @staticmethod
    def use_from_inventory(record):
        inventory = record.game_objects.player.backpack.inventory
        if inventory.get_quantity(record.item_id) <= 0:
            return False

        inventory.remove(record.item_id)
        record.game_objects.player.heal_vitals(1)
        return True

    def pool(game_objects):#all things that should be saved in object pool: #obj = cls.__new__(cls)#creatate without runing initmethod
        HealItem.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/heal_item/',game_objects)
        HealItem.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/items/heal_item/')

    def release_texture(self):#stuff that have pool shuold call this
        pass
