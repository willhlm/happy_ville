import pygame
from engine.utils import read_files
from gameplay.entities.items.base.enemy_drop import EnemyDrop

class AmberDroplet(EnemyDrop):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = AmberDroplet.sprites
        self.sounds = AmberDroplet.sounds

        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'moneyy'

    def player_collision(self,player):#when the player collides with this object
        super().player_collision(player)
        self.game_objects.world_state.update_statistcis('amber_droplet')
        tot_amber = player.backpack.inventory.get_quantity(self)
        self.game_objects.ui.hud.update_money(tot_amber)

    def pool(game_objects):#all things that should be saved in object pool
        AmberDroplet.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/amber_droplet/',game_objects)
        AmberDroplet.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/items/amber_droplet/')

    def set_ui(self):#called from backpask
        self.animation.play('ui')