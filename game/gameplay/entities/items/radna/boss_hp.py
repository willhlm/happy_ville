import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.radna.base_radna import Radna

class BossHP(Radna):
    item_definition = ItemDefinition(
        item_id='boss_hp',
        description='Visible boss HP [2]',
        pickup_text='Visible boss HP [2]',
        pickup_ui_image_path='assets/sprites/ui/pickups/journal/abilityHUD2.png',
    )
    inventory_level = 2

    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = BossHP.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.interact_component.apply_spawn()

    @classmethod
    def entry_on_attach(cls, entry):
        for enemy in entry.owner.game_objects.enemies.sprites():
            enemy.health_bar()#attached a healthbar on boss

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/radna/boss_HP/',game_objects)#for inventor
        super().pool(game_objects)
