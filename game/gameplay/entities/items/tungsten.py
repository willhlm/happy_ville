import pygame
from engine.utils import read_files
from gameplay.entities.items.base.components import ItemInteractComponent, pool_interactable_sprite, InteractionPickupComponent
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.world_item import WorldItem

class Tungsten(WorldItem):
    item_definition = ItemDefinition(
        description='A heavy rock',
    )
    pickup_component_cls = InteractionPickupComponent

    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.interact_component = ItemInteractComponent(self, **kwarg)
        self.sprites = Tungsten.sprites
        self.interact_component.apply_visual_spawn_mode()
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def pickup(self, player):
        self.mark_picked_up()
        player.backpack.inventory.add_item(self.get_item_id())

    def interact(self, player):
        self.interact_component.interact_with_pickup_text(player)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/tungsten/',game_objects)
        pool_interactable_sprite(cls, game_objects)
