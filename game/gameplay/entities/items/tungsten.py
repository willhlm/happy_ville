import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.interact_world_item import InteractWorldItem

class Tungsten(InteractWorldItem):
    item_definition = ItemDefinition(
        item_id='tungsten',
        description='A heavy rock',
        pickup_text='A heavy rock',
        pickup_ui_image_path='assets/sprites/ui/pickups/journal/abilityHUD2.png',
    )
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Tungsten.sprites
        self.interact_component.apply_visual_spawn_mode()
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def pickup(self, player):
        self.mark_picked_up()
        player.backpack.inventory.add_item(self.get_item_id())

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/tungsten/',game_objects)
        cls.pool_interactable_sprite(game_objects)
        cls.pool_pickup_ui_images(game_objects)
