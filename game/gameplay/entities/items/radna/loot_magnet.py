import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.radna.base_radna import Radna

class LootMagnet(Radna):
    item_definition = ItemDefinition(
        item_id='loot_magnet',
        description='Loot magnet [1]',
        pickup_text='Loot magnet [1]',
        pickup_ui_image_path='assets/sprites/ui/pickups/journal/abilityHUD2.png',
    )
    magnet_radius = 120
    magnet_strength = 0.08
    magnet_delay = 150

    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = LootMagnet.sprites
        self.interact_component.apply_visual_spawn_mode()
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

    @classmethod
    def entry_update_equipped(cls, entry):
        player = entry.owner
        player_center = player.hitbox.center
        radius_sq = cls.magnet_radius * cls.magnet_radius
        for item in player.game_objects.loot.sprites():
            if not getattr(item, 'supports_magnet', False):
                continue
            item_delay = getattr(item, 'magnet_delay', 0)
            delay = item_delay if item_delay > 0 else cls.magnet_delay
            if item.age < delay:
                continue

            dx = player_center[0] - item.hitbox.centerx
            dy = player_center[1] - item.hitbox.centery
            if dx * dx + dy * dy > radius_sq:
                continue

            item.velocity[0] = dx * cls.magnet_strength
            item.velocity[1] = dy * cls.magnet_strength

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/radna/loot_magnet/',game_objects)#for inventory
        super().pool(game_objects)
