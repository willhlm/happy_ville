from gameplay.entities.projectiles.base.projectile_clash_results import ProjectileClashResult


class SwordModifierManager:
    def __init__(self, sword):
        self.sword = sword
        self.modifiers = {}
        self._sorted_modifiers = []
        self.registry = {
            'blue_stone': BlueStoneModifier,
            'green_stone': GreenStoneModifier,
            'orange_stone': OrangeStoneModifier,
            'purple_stone': PurpleStoneModifier,
            'red_stone': RedStoneModifier,
        }

    def add_modifier(self, modifier_name, priority=0, **kwargs):
        self.modifiers[modifier_name] = self.registry[modifier_name](self.sword, priority=priority, **kwargs)
        self._sort_modifiers()

    def remove_modifier(self, modifier_name):
        if modifier_name in self.modifiers:
            del self.modifiers[modifier_name]
            self._sort_modifiers()

    def _sort_modifiers(self):
        self._sorted_modifiers = sorted(
            self.modifiers.values(),
            key=lambda modifier: modifier.priority,
            reverse=True,
        )

    def modify_damage(self, damage):
        for modifier in self._sorted_modifiers:
            damage = modifier.modify_damage(damage)
        return damage

    def modify_slash_speed(self, slash_speed):
        for modifier in self._sorted_modifiers:
            slash_speed = modifier.modify_slash_speed(slash_speed)
        return slash_speed

    def modify_hitbox(self, width, height):
        for modifier in self._sorted_modifiers:
            width, height = modifier.modify_hitbox(width, height)
        return width, height

    def on_enemy_hit(self, enemy, effect):
        for modifier in self._sorted_modifiers:
            modifier.on_enemy_hit(enemy, effect)

    def on_projectile_collision(self, projectile):
        for modifier in self._sorted_modifiers:
            if modifier.on_projectile_collision(projectile):
                return

        projectile.projectile_clash.destroy_from(self.sword)

class SwordModifier:
    def __init__(self, sword, priority=0):
        self.sword = sword
        self.priority = priority

    def modify_damage(self, damage):
        return damage

    def modify_slash_speed(self, slash_speed):
        return slash_speed

    def modify_hitbox(self, width, height):
        return width, height

    def on_enemy_hit(self, enemy, effect):
        return

    def on_projectile_collision(self, projectile):
        return False


class BlueStoneModifier(SwordModifier):
    def on_enemy_hit(self, enemy, effect):
        self.sword.entity.gain_spirit(1)


class GreenStoneModifier(SwordModifier):
    def modify_slash_speed(self, slash_speed):
        return slash_speed * 1.32


class OrangeStoneModifier(SwordModifier):
    def modify_hitbox(self, width, height):
        return width + 35, height + 11


class PurpleStoneModifier(SwordModifier):
    def on_projectile_collision(self, projectile):
        projectile.projectile_clash.reflect_from(
            self.sword,
            self.sword.dir,
            self.sword.hitbox.center,
            team=self.sword.team,
        )
        return True


class RedStoneModifier(SwordModifier):
    def modify_damage(self, damage):
        return damage * 1.1
