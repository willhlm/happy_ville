import pygame
from engine.utils import read_files
from gameplay.entities.items.base.enemy_drop import EnemyDrop

class Bone(EnemyDrop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Bone.sprites
        self.sounds = Bone.sounds
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1],16,16)

        self.hitbox.midbottom = self.rect.midbottom
        self.true_pos = list(self.rect.topleft)
        self.description = 'Ribs from my daugther. You can respawn and stuff'

    def use_item(self):
        if self.game_objects.player.backpack.inventory.get_quantity('bone') <= 0: return#if we don't have bones
        self.game_objects.player.backpack.inventory.remove('bone')
        self.game_objects.player.backpack.map.save_bone(map = self.game_objects.map.level_name, point = self.game_objects.camera_manager.camera.scroll)
        self.game_objects.player.currentstate.enter_state('Plant_bone_main')

    def pool(game_objects):#all things that should be saved in object pool
        Bone.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/bone/',game_objects)
        Bone.sounds = read_files.load_sounds_dict('assets/audio/sfx/audio/sfx/enteties/items/bone/')

    def release_texture(self):#stuff that have pool shuold call this
        pass