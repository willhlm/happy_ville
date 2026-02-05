import pygame

from gameplay.entities.projectiles.base.melee import Melee
from engine.utils import read_files
from . import states_sword
from engine import constants as C
from gameplay.entities.shared.components import hit_effects

class Sword(Melee):
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/aila_sword/',self.entity.game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/projectiles/sword/')
        self.image = self.sprites['slash_1'][0]
        self.animation.play('slash_1')
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_sword.Slash_1(self)

        self.tungsten_cost = 1#the cost to level up to next level
        self.stones = {}#{'red': Red_infinity_stone([0,0], entity.game_objects, entity = self), 'green': Green_infinity_stone([0,0], entity.game_objects, entity = self), 'blue': Blue_infinity_stone([0,0],entity.game_objects, entity = self),'orange': Orange_infinity_stone([0,0],entity.game_objects, entity = self),'purple': Purple_infinity_stone([0,0], entity.game_objects, entity = self)}#gets filled in when pick up stone. used also for inventory
        self.swing = 0#a flag to check which swing we are at (0 or 1)
        self.stone_states = {'enemy_collision': states_sword.Stone_states(self), 'projectile_collision': states_sword.Stone_states(self), 'slash': states_sword.Stone_states(self)}#infinity stones can change these to do specific things

    def use_sword(self, swing = 'light'):#called from player stetas whenswing sword
        self.stone_states['slash'].slash_speed()
        self.entity.game_objects.sound.play_sfx(self.entity.sword.sounds['swing'][0])

    def update_hitbox(self):
        hitbox_attr, entity_attr = self.direction_mapping[tuple(self.dir)]#self.dir is set in states_sword
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate.update_rect()

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with projectile
        effect = self.create_effect()
        self.stone_states['projectile_collision'].projectile_collision(eprojectile, effect)

    def collision_enemy(self, enemy):#latest collision version
        effect = self.create_effect()
        self.currentstate.sword_jump()

        damage_applied, modified_effect = enemy.take_hit(effect)
        if damage_applied:#if damage was applied
            self.stone_states['enemy_collision'].enemy_collision()

    def collision_interactables(self, inetractable):#latest collision version
        self.currentstate.sword_jump()
        effect = self.create_effect()
        damage_applied, modified_effect = inetractable.take_hit(effect)

    def level_up(self):#called when the smith imporoves the sword
        self.entity.inventory['Tungsten'] -= self.tungsten_cost
        self.dmg *= 1.2
        self.tungsten_cost += 2#1, 3, 5 tungstes to level up

    def draw(self, target):
        pass

    def create_effect(self):
        """Create sword hit effect with current damage values"""
        particle = {
            'lifetime': 180,
            'scale': 5,
            'angle_spread': [13, 15],
            'angle_dist': 'normal',
            'colour': C.spirit_colour,
            'gravity_scale': -0.1,
            'gradient': 1,
            'fade_scale': 2.2,
            'number_particles': 8,
            'vel': {'ejac': [13, 17]},
            'dir': self.dir
        }
        
        return hit_effects.create_melee_effect(
            damage=self.dmg,
            hit_type='sword',
            knockback=[25, 10],
            hitstop=5,
            particles=particle,
            attacker=self.entity,
            projectile=self,
            meta = {'attacker_dir': self.dir},#save direction
        )