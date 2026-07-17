import random
from .base_composite import CompositeState
from .base_state import PhaseAirBase
from engine import constants as C

class AirGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': AirGlidePre(entity), 'main': AirGlideMain(entity)}

    def update(self, dt): 
        self.current_phase.update(dt)

class AirGlidePre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.enable_glide()
        self.entity.velocity[1] = 0
        self.entity.animation.play('fall_pre')
        self.entity.game_objects.particles.emit(
            "enemy_death_burst",
            pos=self.entity.hitbox.center,
            n=30,
            colour=[255,255,255,255],
        )

    def exit(self):
        self.disable_glide()

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
            self.enter_state('fall')

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

    def update(self, dt):
        dx = random.uniform(-1, 1) * 20
        dy = random.uniform(-1, 1) * 20
        position = [self.entity.hitbox.centerx + dx, self.entity.hitbox.centery + dy]
        self.entity.game_objects.particles.emit(
            "tiny_trail",
            pos=position,
            n=1,
            colour=C.spirit_colour,
            dir=[0, 1],
            vx=self.entity.velocity[0] * 0.1,
            vy=self.entity.velocity[1] * 0.1,
        )

    def enable_glide(self):
        if 'shield_glide' not in self.entity.movement_modifier.modifiers:
            self.entity.movement_modifier.add_modifier('shield_glide')

    def disable_glide(self):
        self.entity.movement_modifier.remove_modifier('shield_glide')

    def consume_contact_state(self):
        if self.entity.is_on_floor():
            if self.entity.acceleration[0] != 0:
                self.enter_state('run')
            else:
                self.enter_state('land', phase='soft')
            return

        if self.entity.has_wall_glide_collision():
            self.enter_state('wall_glide')

class AirGlideMain(AirGlidePre):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.enable_glide()
        self.entity.animation.play('fall_main')

    def increase_phase(self):
        pass
