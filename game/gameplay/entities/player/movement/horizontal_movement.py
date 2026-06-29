from engine import constants as C
from engine.utils.functions import sign


class HorizontalMovement:
    def __init__(self, entity):
        self.entity = entity
        self.input_x = 0
        self.intent_sign = 0

    def apply_ground_input(self, axes, allow_facing_update=True):
        value = axes.move
        self._store_input(value[0])

        multiplier = 0
        if 0.1 < abs(value[0]) < 0.65:
            multiplier = 0.3
        elif abs(value[0]) >= 0.65:
            multiplier = 1

        self.entity.acceleration[0] = C.acceleration[0] * multiplier
        self.entity.dir[1] = -value[1]
        if allow_facing_update and multiplier > 0:
            self.entity.dir[0] = self.intent_sign

    def apply_air_input(self, axes, allow_facing_update=True):
        value = axes.move
        self._store_input(value[0])

        multiplier = 1 if abs(value[0]) > 0.1 else 0
        self.entity.acceleration[0] = C.acceleration[0] * multiplier
        self.entity.dir[1] = -value[1]
        if allow_facing_update and multiplier > 0:
            self.entity.dir[0] = self.intent_sign

    def has_intent(self):
        return self.intent_sign != 0

    def get_drive_direction(self, fallback_dir):
        if self.has_intent():
            return self.intent_sign
        return fallback_dir

    def _store_input(self, input_x):
        self.input_x = input_x
        self.intent_sign = sign(input_x) if abs(input_x) > 0.1 else 0
