from .base_state import PhaseAirBase, PhaseBase
from engine import constants as C

class Sword(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['attack_able'] = False
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()

class SwordAir(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['attack_able'] = False
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()
