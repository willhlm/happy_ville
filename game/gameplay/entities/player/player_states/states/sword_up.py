from .base_composite import CompositeState
from .sword_base import Sword
from engine import constants as C

class SwordUpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordUpMain(entity)}

class SwordUpMain(Sword):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sword_up_main')
        self.entity.flags['attack_able'] = False
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()
        self.entity.sword.currentstate.enter_state('Slash_up')
        self.entity.projectiles.add(self.entity.sword)

    def increase_phase(self):
        if self.entity.collision_types['bottom']:
            if self.entity.acceleration[0] == 0:
                self.enter_state('idle')
            else:
                self.enter_state('run')
        else:
            self.enter_state('fall')