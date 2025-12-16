
from engine import constants as C
from engine.utils.functions import sign

#normal phases
class PhaseBase():
    def __init__(self, entity):
        self.entity = entity

    def update(self, dt):
        pass

    def increase_phase(self):
        pass

    def handle_input(self, input, **kwarg):
        pass

    def enter(self, **kwarg):#called when entering a new phase
        pass

    def exit(self):
        """Called exactly once when exiting this phase."""
        pass        

    def enter_state(self, new_state, **kwarg):#should call when entering a new state
        self.entity.currentstate.enter_state(new_state, **kwarg)

    def enter_phase(self, phase_name, **kwarg):#should call when just changing phase
        self.entity.currentstate.composite_state.enter_phase(phase_name, **kwarg)

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_release_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press

        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        multiplier = 0
        if 0.1 < abs(value[0]) < 0.65:
            multiplier = 0.3
        elif abs(value[0]) >= 0.65:
            multiplier = 1
        self.entity.acceleration[0] = C.acceleration[0] * multiplier#always positive, add acceleration to entity

        self.entity.dir[1] = -value[1]
        if multiplier > 0:
            self.entity.dir[0] = sign(value[0])

    def do_ability(self):#called when pressing B (E). This is needed if all of them do not have pre animation, or vice versa
        self.enter_state(self.entity.abilities.equip.lower())

class PhaseAirBase(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press

        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        multiplier = 0
        if abs(value[0]) > 0.1:
            multiplier = 1
        self.entity.acceleration[0] = C.acceleration[0] * multiplier#always positive, add acceleration to entity

        self.entity.dir[1] = -value[1]
        if multiplier > 0:
            self.entity.dir[0] = sign(value[0])

class NullPhase(PhaseBase):
    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    def update(self, dt):
        pass                 