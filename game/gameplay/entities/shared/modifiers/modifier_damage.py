from gameplay.entities.shared.components.hit_results import HitResult

class DamageManager():
    """Manages damage modifiers (for player, complex entities)"""
    
    def __init__(self, entity):
        self.entity = entity
        self.modifiers = {}
        self._sorted_modifiers = []
        
        # Registry of available modifiers
        self.registry = {
            'half_dmg': HalfDamageModifier,
            'tjasolmais_embrace': ShieldModifier,
            'parry_window': ParryModifier
        }

    def add_modifier(self, modifier_name, priority=0, **kwargs):
        """Add a modifier by name from registry"""
        self.modifiers[modifier_name] = self.registry[modifier_name](priority, **kwargs)
        self._sort_modifiers()

    def remove_modifier(self, modifier_name):
        """Remove a modifier by name"""
        if modifier_name in self.modifiers:
            del self.modifiers[modifier_name]
            self._sort_modifiers()

    def clear_modifiers(self):
        """Remove all modifiers"""
        self.modifiers.clear()
        self._sorted_modifiers.clear()

    def _sort_modifiers(self):
        """Sort modifiers by priority (highest first)"""
        self._sorted_modifiers = sorted(
            self.modifiers.values(), 
            key=lambda m: m.priority, 
            reverse=True
        )   

class HitModifier():
    """Base class for hit modifiers"""
    def __init__(self, priority):
        self.priority = priority

    def modify_hit(self, effect):
        """Modify the hit effect. Can change damage, cancel hit, etc."""
        pass

class HalfDamageModifier(HitModifier):
    """Reduces damage by half"""
    def __init__(self, priority=0):
        super().__init__(priority)

    def modify_hit(self, effect):
        effect.damage *= 0.5

class ShieldModifier(HitModifier):
    """Shield absorbs damage instead of entity"""
    def __init__(self, priority, entity):
        super().__init__(priority)
        self.entity = entity

    def modify_hit(self, effect):
        # Shield takes damage instead
        self.entity.abilities.spirit_abilities['Shield'].shield.take_damage(effect.damage)
        effect.result = HitResult.BLOCKED  # Cancel damage to main entity

class ParryModifier(HitModifier):
    """Active parry window that cancels hits"""
    def __init__(self, priority=100):  # High priority
        super().__init__(priority)
        self.active_frames = 0

    def activate(self, duration=10):
        """Start parry window"""
        self.active_frames = duration

    def update(self):
        """Call each frame"""
        if self.active_frames > 0:
            self.active_frames -= 1

    def modify_hit(self, effect):
        if self.active_frames > 0:
            effect.result = HitResult.PARRIED

class SuperArmorModifier(HitModifier):#exaple showing
    """Super armor - takes damage but no knockback, light hitstop"""
    def __init__(self, priority=30):
        super().__init__(priority)
    
    def modify_hit(self, effect):# Replace callbacks with class methods        
        effect.defender_callbacks['hitstop'] = self.super_armor_hitstop
        effect.attacker_callbacks['hitstop'] = self.light_attacker_hitstop
    
    def super_armor_hitstop(self, defender, effect, attacker_dir):
        """Light hitstop without knockback"""
        defender.apply_hitstop(lifetime=3, call_back = None)
    
    def light_attacker_hitstop(self, projectile, effect, defender):
        """Reduced attacker hitstop"""
        projectile.attacker.apply_hitstop(lifetime=2)    