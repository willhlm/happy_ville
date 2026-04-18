from .base_composite import CompositeState
from .base_state import PhaseBase
from engine import constants as C

class IdleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': IdleMain(entity)}

class IdleMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('idle', f_rate = 0.1667)
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        if input.name == 'a':
            input.processed()
            self.enter_state('jump')
        elif input.name == 'lb':
            input.processed()
            self.enter_state('dash_ground')
        elif input.name == 'x':
            if input.meta.get('smash') and False:
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
        elif input.name == 'b':
            input.processed()
            self.do_ability()
        elif input.name == 'rt':
            input.processed()
            self.enter_state('heal')

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()

    def handle_movement(self, axes):
        super().handle_movement(axes)
        if abs(self.entity.acceleration[0]) > 0.5:
            self.enter_state('run')
        elif abs(self.entity.acceleration[0]) > 0.1:
            self.enter_state('walk')

    def swing_sword(self):
        if not self.entity.flags['attack_able']:
            return
        if self.entity.dir[1] == 0:
            state = 'sword_stand' + str(int(self.entity.sword.swing) + 1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0:
            self.enter_state('sword_up')