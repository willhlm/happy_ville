from .base_composite import CompositeState
from .base_state import PhaseAirBase
from engine import constants as C

class FallState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': FallPre(entity), 'main': FallMain(entity)}

    def common_values(self):
        self.falltime = 0

    def update(self, dt):
        self.falltime += dt
        self.current_phase.update(dt)

    def determine_fall(self):
        return self.falltime >= 4000

    def determine_sprint(self):
        return self.entity.flags['sprint_chain_active']

class FallPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_pre')

    def handle_press_input(self, input):
        if input.name == 'a':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('jump')
        elif input.name == 'b':
            input.processed()
            self.do_ability()
        elif input.name == 'lb':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('dash_ground')
            else:
                input.processed()
                self.enter_state('dash_air')
        elif input.name == 'x':
            input.processed()
            self.swing_sword()

    def handle_release_input(self, input):
        if input.name == 'a':
            input.processed()
        elif input.name == 'lb':
            self.entity.flags['sprint_chain_active'] = False
            input.processed()

    def handle_movement(self, axes):
        if self.entity.game_objects.controller.is_held('lb') and self.entity.currentstate.states['fall'].determine_sprint():
            value = axes.move
            multiplier = C.sprint_multiplier if abs(value[0]) > 0.1 else 0
            self.entity.acceleration[0] = C.acceleration[0] * multiplier
            self.entity.dir[1] = -value[1]
            if abs(value[0]) > 0.1:
                self.entity.dir[0] = 1 if value[0] > 0 else -1
            return

        super().handle_movement(axes)

    def swing_sword(self):
        if not self.entity.flags['attack_able']:
            return
        if self.entity.dir[1] > C.down_angle:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < C.down_angle * -1:
            self.enter_state('sword_down')
        else:
            state = 'sword_air' + str(self.entity.combat_tracker.next_swing_index())
            self.enter_state(state)

    def increase_phase(self):
        self.enter_phase('main')

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            should_sprint = self.entity.game_objects.controller.is_held('lb') and self.entity.currentstate.states['fall'].determine_sprint()
            self.entity.flags['sprint_chain_active'] = False
            if self.entity.currentstate.states['fall'].determine_fall():
                self.enter_state('land', phase='hard')
            elif should_sprint:
                self.enter_state('sprint')
            elif self.entity.acceleration[0] != 0:
                self.enter_state('run')
            else:
                self.enter_state('land', phase='soft')
            return

        if self.entity.has_collision_kind('belt'):
            self.enter_state('belt_glide')
            return

        if self.entity.has_collision_kind('Wall'):
            self.enter_state('wall_glide')

class FallMain(FallPre):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_main')

    def increase_phase(self):
        pass
