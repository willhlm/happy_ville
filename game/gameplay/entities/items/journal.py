import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.interact_world_item import InteractWorldItem

class Journal(InteractWorldItem):#journal with kills
    item_definition = ItemDefinition(
        item_id='journal',
        description='A journal',
        title='Hunter\'s Journal',
        pickup_text='Open the menu and navigate to the journal tab. Defeat enemies to add them to the journal.',
        pickup_ui_image_path='assets/sprites/ui/overlay/items/journal/journal.png',
    )
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = Journal.sprites  
        self.interact_component.apply_visual_spawn_mode()
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def pickup(self, player):
        player.backpack.add_holding('journal')            
        self.mark_picked_up()
        self.kill()

    @classmethod
    def pool(cls, game_objects):                
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/journal/',game_objects)
        cls.pool_interactable_sprite(game_objects)
        cls.pool_pickup_ui_images(game_objects)
        
