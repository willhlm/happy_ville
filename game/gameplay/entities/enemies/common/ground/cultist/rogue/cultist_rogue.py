import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import states_rogue_cultist
from gameplay.entities.projectiles import HurtBox

class CultistRogue(Enemy):
    kill_signal = 'cultist_killed'

    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = CultistRogue.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 40, 40)
        self.vitals.set_max_health(3)
        self.vitals.set_health(self.vitals.max_health)
        self.attack_distance = [80,10]
        self.currentstate = states_rogue_cultist.Idle(self)

    def pool(game_objects):
        CultistRogue.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/cultist_rogue/',game_objects)

    def release_texture(self):
        pass

    def attack(self):#called from states, attack main
        self.game_objects.projectiles.add_enemy(HurtBox(self))#add to group
