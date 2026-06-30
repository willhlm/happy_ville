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
        self.move_dir_x = entity.dir[0]

    def enter(self, **kwarg):
        self.move_dir_x = self.entity.dir[0]
        self.entity.animation.play(self.animation_name)        
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.use_sword()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.game_objects.projectiles.add_friendly(self.entity.sword)

    def increase_phase(self):
        self.enter_state('fall')

    def handle_movement(self, axes):#all states should inehrent this function: called in update function of gameplay state
        value = axes.move
        self.entity.acceleration[0] = C.acceleration[0] if abs(value[0]) > 0.1 else 0
        self.entity.dir[1] = -value[1]
        if self.entity.acceleration[0] != 0:
            self.move_dir_x = sign(value[0])

    def handle_input(self, input, **kwarg):
        pass

    def get_move_dir_x(self):
        return self.move_dir_x

    def consume_contact_state(self):
        if not self.entity.is_on_floor():
            return
        if self.entity.acceleration[0] != 0:
            self.enter_state('run')
        else:
            self.enter_state('idle')
