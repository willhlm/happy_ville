from .base_ability import Ability
from engine import constants as C
from engine.utils import read_files
from gameplay.entities.projectiles import Shield

class TjasolmaisEmbrace(Ability):#makes the shield, water god
    id = 'shield'
    name = 'Shield'
    state_name = 'shield'
    spirit_cost = 1
    selectable = True
    max_level = 2
    unlock_boss_id = 'tjasolmai'

    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/tjasolmais_embrace/',entity.game_objects)
        self.description = [
            'Summon a shield that absorbs incoming damage.',
            'Hold jump while shielded to slow your fall.',
        ]
        self.active_shield = None

    def has_active_shield(self):
        return self.active_shield is not None

    def clear_active_shield(self):
        self.disable_glide()
        self.entity.hit_component.damage_manager.remove_modifier('tjasolmais_embrace')
        self.active_shield = None

    def cancel_active_shield(self):
        if self.has_active_shield():
            self.active_shield.kill()

    def on_sword_attack(self):
        self.cancel_active_shield()

    def absorb_hit(self, effect):
        if not self.has_active_shield():
            return
        self.active_shield.take_dmg(effect.damage)

    def can_glide(self):
        return self.is_at_least_level(1)# and self.has_active_shield()

    def is_fall_state_active(self):
        return self.entity.currentstate.composite_state is self.entity.currentstate.states.get('fall')

    def should_glide(self):
        if not self.can_glide():
            return False
        if not self.is_fall_state_active():
            return False
        return self.entity.game_objects.controller.is_held('a')

    def enable_glide(self):
        if 'shield_glide' not in self.entity.movement_modifier.modifiers:
            self.entity.movement_modifier.add_modifier('shield_glide')

    def disable_glide(self):
        self.entity.movement_modifier.remove_modifier('shield_glide')

    def initiate(self):#called when using the abilty
        self.cancel_active_shield()
        self.active_shield = Shield(self.entity, ability=self, health=self.get_shield_health())
        self.disable_glide()
        self.entity.hit_component.damage_manager.add_modifier('tjasolmais_embrace', entity = self.entity)
        self.entity.game_objects.projectiles.add_friendly(self.active_shield)

    def get_shield_health(self):
        return 1

    def update(self, dt):
        if self.should_glide():
            self.enable_glide()
            self.entity.game_objects.particles.emit(
                "spirit_wisp",
                pos=self.entity.hitbox.center,
                n=1,
                colour=C.spirit_colour,
            )
            return
        self.disable_glide()
