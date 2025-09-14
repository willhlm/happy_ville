import pygame
from engine.utils import read_files
from gameplay.entities.items.base.enemy_drop import EnemyDrop

class HealItem(EnemyDrop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = HealItem.sprites
        self.sounds = HealItem.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1],16,16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'Use it to heal'

    def use_item(self):
        if self.game_objects.player.backpack.inventory.get_quantity('heal_item') < 0: return
        self.game_objects.player.backpack.inventory.remove('heal_item')
        self.game_objects.player.heal(1)

    def pool(game_objects):#all things that should be saved in object pool: #obj = cls.__new__(cls)#creatate without runing initmethod
        HealItem.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/heal_item/',game_objects)
        HealItem.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/items/heal_item/')

    def release_texture(self):#stuff that have pool shuold call this
        pass