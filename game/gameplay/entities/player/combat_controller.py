from engine import constants as C


class CombatController:
    def __init__(self, entity):
        self.entity = entity
        self.swing = 0
        self.sword_movesets = {
            "ground": self._resolve_ground_sword,
            "air": self._resolve_air_sword,
        }

    def resolve_sword_attack(self, moveset_name):
        if not self.entity.flags["attack_able"]:
            return None

        return self.sword_movesets[moveset_name]()

    def _resolve_ground_sword(self):
        vertical_direction = self.entity.dir[1]
        if vertical_direction > C.down_angle:
            return "sword_up"

        if vertical_direction < -C.down_angle:
            return None

        return self._next_neutral_sword("sword_stand")

    def _resolve_air_sword(self):
        vertical_direction = self.entity.dir[1]
        if vertical_direction > C.down_angle:
            return "sword_up"

        if vertical_direction < -C.down_angle:
            return "sword_down"

        return self._next_neutral_sword("sword_air")

    def _next_neutral_sword(self, state_prefix):
        return f"{state_prefix}{self.next_swing_index()}"

    def next_swing_index(self):
        current = int(self.swing) + 1
        self.swing = not self.swing
        return current
