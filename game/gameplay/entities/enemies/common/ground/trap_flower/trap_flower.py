import pygame
from engine.utils.functions import sign
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG
from .states import AttackPre, AttackMain, AttackPost

TRAP_FLOWER_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
}

class TrapFlower(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['trap_flower']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/trap_flower/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)        

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type='ground', custom_states=TRAP_FLOWER_STATES)
        self.flags['aggro'] = False

        self.bloom_light = self.game_objects.lights.create(self, radius=70, colour=[255, 255, 255, 255])
        self.shader_state.add_shader('glow', colour=(132 / 255, 255 / 255, 246 / 255), intensity=0.9, radial_center=(30/64, (48-37)/48), radial_inner=0.03, radial_outer=0.1)

    def player_collision(self, player):
        if self.currentstate.cooldowns.get("melee_attack") > 0:
            return

        state = getattr(self.currentstate, "state", None)
        if state is not None and state.config_key in {"attack_pre", "attack_main", "attack_post", "death", "dead", "hurt"}:
            return

        self.currentstate.enter_state("attack_pre")

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = [0,0], size = [32, 32])#make the object
        self.game_objects.projectiles.add_enemy(attack)#add to group but in main phase

    def knock_back(self, amp, dir):
        pass
