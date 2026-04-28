import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.interact_world_item import InteractWorldItem
from .config import DYES, PALETTE_CHANNELS

class Dyes(InteractWorldItem):#ring in which to attach radnas
    item_definition = ItemDefinition(
        item_id='dyes',
        description='A dye',
        pickup_text='A dye',
        pickup_ui_image_path='assets/sprites/ui/pickups/journal/abilityHUD2.png',
    )
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.name = kwarg['name']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/dyes/' + self.name + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        dye_config = DYES[self.name]
        self.channel = dye_config['channel']
        self.target_colour = PALETTE_CHANNELS[self.channel]['source']
        self.replace_colour = dye_config['target']

    def pickup(self, player):
        self.mark_picked_up()
        player.backpack.inventory.add_dye(self)

    def get_pickup_persistence_key(self):
        return self.name

    @classmethod
    def pool(cls, game_objects):
        cls.pool_pickup_ui_images(game_objects)
