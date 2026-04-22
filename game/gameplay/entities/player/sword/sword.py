import pygame, random

from gameplay.entities.projectiles.base.melee import Melee
from gameplay.entities.shared.components.body.melee_body import SwordBody
from engine.utils import read_files
from . import states_sword
from engine import constants as C
from gameplay.entities.shared.components.hit import hit_effects
from gameplay.entities.player.sword.modifier_sword import SwordModifierManager

class Sword(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/aila_sword/',self.entity.game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/projectiles/sword/')
        self.image = self.sprites['slash_1'][0]        
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        
        self.body = SwordBody(self)
        self.base_damage = self.dmg        
        self.modifier_manager = SwordModifierManager(self)
        self.currentstate = states_sword.Slash_1(self)
        
        self.level = 0

    def use_sword(self, swing = 'light'):#called from player stetas whenswing sword
        self.entity.animation.framerate = self.modifier_manager.modify_slash_speed(self.entity.animation.framerate)
        self.entity.game_objects.sound.play_sfx(self.entity.sword.sounds['swing'][0])

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with projectile
        self.modifier_manager.on_projectile_collision(eprojectile)

    def collision_enemy(self, enemy):#latest collision version
        effect = self.create_effect()

        damage_applied, modified_effect = enemy.take_hit(effect)
        if damage_applied:#if damage was applied
            self.modifier_manager.on_enemy_hit(enemy, modified_effect)

    def collision_interactables(self, inetractable):#latest collision version
        effect = self.create_effect()
        damage_applied, modified_effect = inetractable.take_hit(effect)

    def create_effect(self):
        """Create sword hit effect with current damage values"""
        defender_particle = {
            "preset": "sword_hit",
            "n": 8,
            "args": {
                "dir": self.dir,
                "colour": C.spirit_colour,                    
            },
        }

        attacker_particles= {
            "preset": "sword_clash",
            "n": 5,  
            "args": {
                "angle": random.randint(-180, 180),  # old clash random angle
                "colour": [255, 255, 255, 255],            
            },
        }

        effect = hit_effects.create_melee_effect(self.entity.game_objects,
            damage=self.get_damage(),
            hit_type='sword',
            knockback=[25, 10],
            hitstop=5,
            particles=defender_particle,#defender
            attacker_particles = attacker_particles,
            attacker=self.entity,
            projectile=self,
            attacker_dir=self.dir,
        )

        effect.attacker_callbacks['sword_jump'] = lambda eff: eff.projectile.currentstate.sword_jump()#add sword jump
        return effect

    def level_up(self):#called when the smith imporoves the sword
        self.entity.inventory['Tungsten'] -= self.get_upgrade_cost()
        self.base_damage *= 1.2
        self.level += 1

    def get_upgrade_cost(self):
        return 1 + self.level * 2

    def get_damage(self):
        return self.modifier_manager.modify_damage(self.base_damage)

    def apply_hitbox_size(self, width, height):
        width, height = self.modifier_manager.modify_hitbox(width, height)
        self.hitbox[2] = width
        self.hitbox[3] = height

    def draw(self, target):
        pass        
