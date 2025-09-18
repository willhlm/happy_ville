import sys

class DamageManager():
    def __init__(self, entity):
        self.entity = entity
        self.modifiers = {}
        self._sorted_modifiers = []        

    def add_modifier(self, modifier, priority=0, **kwarg):
        new_modifier = getattr(sys.modules[__name__], modifier)(priority, **kwarg)
        self.modifiers[modifier] = new_modifier
        self._sort_modifiers()

    def remove_modifier(self, modifier):
        del self.modifiers[modifier]
        self._sort_modifiers()

    def take_dmg(self, dmg, effects):
        if self.entity.flags["invincibility"]: return False            

        context = Damage_context(dmg, effects)

        for modifier in self._sorted_modifiers:
            modifier.take_dmg(context)
            if context.cancelled: return False                

        self.entity.apply_damage(context)
        return True

    def clear_modifiers(self):
        self.modifiers.clear()

    def _sort_modifiers(self):
        self._sorted_modifiers = sorted(self.modifiers.values(), key = lambda m: m.priority, reverse = True)        

class Damage_context():
    def __init__(self, dmg, effects):        
        self.dmg = dmg
        self.effects = effects
        self.cancelled = False

class Modifier():
    def __init__(self, priority):
        self.priority = priority

    def take_dmg(self, context):
        pass  

class Half_dmg(Modifier):#appended when half damage omamori is equipped
    def __init__(self, priority):
        super().__init__(priority)

    def take_dmg(self, context):
        context.damage *= 0.5

class Tjasolmais_embrace(Modifier):#appended when tjasolmais embrace is equipped
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']

    def take_dmg(self, context):        
        self.entity.abilities.spirit_abilities['Shield'].shield.take_dmg(context.damage)   #shieidl takes damage instead of entity     
        context.cancelled = True

class Parry_window(Modifier):
    def __init__(self, priority):
        super().__init__(priority)
        self.active_frames = 10

    def update(self):
        if self.active_frames > 0:
            self.active_frames -= 1

    def take_dmg(self, context):
        if self.active_frames > 0:
            context.cancelled = True
            context.meta["parried"] = True        