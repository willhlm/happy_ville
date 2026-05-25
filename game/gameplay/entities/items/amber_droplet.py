import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.components import ItemLifetimeComponent
from gameplay.entities.items.base.collision_world_item import CollisionWorldItem

class AmberDroplet(CollisionWorldItem):
    item_definition = ItemDefinition(
        item_id='amber_droplet',
        description='moneyy',
        inventory_animation_name='ui',
    )
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.lifetime_component = ItemLifetimeComponent(self, lifetime=500)
        self.sprites = AmberDroplet.sprites
        self.sounds = AmberDroplet.sounds

        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)

    def pickup(self, player):
        self.add_to_inventory(player)

        self.game_objects.world_state.statistics_state.update_statistic('amber_droplet')

        tot_amber = player.backpack.inventory.get_quantity(self.get_item_id())
        self.game_objects.ui.hud.meters.update_money(tot_amber)

        self.game_objects.sound.play_sfx(self.sounds['death'][0], vol=0.3)

        self.game_objects.particles.emit("pick_up_spark", pos = self.hitbox.center, n=2, colour = [255, 240, 180, 255])
        self.kill()
        #self.currentstate.handle_input('death')


    def pool(game_objects):#all things that should be saved in object pool
        AmberDroplet.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/amber_droplet/',game_objects)
        AmberDroplet.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/items/amber_droplet/')
