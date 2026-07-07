import pygame, random
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.enemies.common.shared.effects.death_effects import ShadowEnemyDeathEffect
from .config import ENEMY_CONFIG as GHOUL_CONFIG

from .states import Spawn, Invisible

GHOUL_STATES = {
    'spawn': Spawn,
    'invisible': Invisible, #placeholder
}

class Ghoul(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.config = GHOUL_CONFIG['ghoul']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/ghoul/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type = 'ground', custom_states = GHOUL_STATES)

        self.shader_state.add_shader('aura', colour = [0,0,0], size = 0.3, fall_off = 4, noise_intensity = 3)
        self.time = 0

        self.death_effects = ShadowEnemyDeathEffect(self) ##change this to shadowEnemydeatheffect

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 5, dir = self.dir, size = [32, 32])#make the object
        self.game_objects.projectiles.add_enemy(attack)#add to group but in main phase

    def update_render(self, dt):
        super().update_render(dt)
        self.release_particles(dt)

    def release_particles(self, dt):
        self.time += dt
        if self.time > 40:
            rect = self.hitbox
            position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(rect[3]*0.1,rect[3]*0.5)]
            self.game_objects.particles.emit("spirit_wisp", pos=position, n=1, colour=(0,0,0,255))
            self.time = 0
