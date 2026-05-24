from .base_composite import CompositeState
from .sword_base import SwordAir
from engine import constants as C
from engine.utils.functions import sign

class SwordAir1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air1_main')}

class SwordAir2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air2_main')}

class SwordAirMain(SwordAir):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']
        self.move_dir = 0

    def enter(self, **kwarg):
        self.move_dir = 0
        self.entity.animation.play(self.animation_name)        
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.use_sword()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.game_objects.projectiles.add_friendly(self.entity.sword)

    def update(self, dt):
        # Keep attack facing committed while preserving normal horizontal air control.
        self.entity.velocity[0] += dt * C.acceleration[0] * self.move_dir

    def increase_phase(self):
        self.enter_state('fall')

    def handle_movement(self, axes):#all states should inehrent this function: called in update function of gameplay state
        value = axes.move#the avlue of the press

        self.move_dir = sign(value[0]) if abs(value[0]) > 0.1 else 0
        self.entity.acceleration[0] = 0
        self.entity.dir[1] = -value[1]

    def handle_input(self, input, **kwarg):
        pass

    def consume_contact_state(self):
        if not self.entity.is_on_floor():
            return
        if self.move_dir != 0:
            self.enter_state('run')
        else:
            self.enter_state('idle')
