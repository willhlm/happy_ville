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

    def handle_movement(self, axes):#all states should inehrent this function: called in update function of gameplay state
        self.entity.movement_controller.apply_ground_movement(axes)

    def do_ability(self):#called when pressing B (E).
        self.entity.abilities.enter_equipped_state(self.enter_state)

    def consume_contact_state(self):
        pass

class PhaseAirBase(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self, axes):#all states should inehrent this function: called in update function of gameplay state
        self.entity.movement_controller.apply_air_movement(axes)

class NullPhase(PhaseBase):
    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    def update(self, dt):
        pass                 
