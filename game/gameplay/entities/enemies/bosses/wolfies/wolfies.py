import pygame 
from gameplay.entities.enemies.base.boss import Boss
from engine.utils import read_files
from gameplay.entities.enemies.bosses import task_manager
from gameplay.entities.projectiles import HurtBox
from . import wolfies_states
from gameplay.entities.projectiles.chain_projectile import ChainProjectile
from gameplay.entities.projectiles import SlamAttack

class Wolfies(Boss):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/bosses/wolfies/',game_objects, flip_x = True)
        self.image = self.sprites['idle_nice'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 35, 45)
        self.health = 2

        self.currentstate = task_manager.TaskManager(self, wolfies_states.STATE_REGISTRY, wolfies_states.PATTERNS)

        self.ability = 'dash_ground_main'#the stae of image that will be blitted to show which ability that was gained
        
        self.attack_distance = [100, 50]
        self.jump_distance = [240, 50]

        self.light = self.game_objects.lights.add_light(self, radius = 150)

    def give_abillity(self):#called when reindeer dies
        self.game_objects.player.currentstate.unlock_state('dash')#append dash abillity to available states
        self.game_objects.world_state.cutscene_complete('boss_deer_encounter')#so not to trigger the cutscene again        

    def kill(self):
        super().kill()
        self.game_objects.lights.remove_light(self.light)#should be removed when reindeer is removed from the game

    def attack(self, lifetime = 10):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = self.dir, size = [32, 32])#make the object
        self.game_objects.eprojectiles.add(attack)#add to group but in main phase

    def slam_attack(self):#called from states, attack main
        self.game_objects.cosmetics.add(ChainProjectile(self.rect.center, self.game_objects, SlamAttack, direction = self.dir, distance = 50, number = 5, frequency = 20))
