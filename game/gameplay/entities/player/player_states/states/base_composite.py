from .base_state import NullPhase

class CompositeState():#will contain pre, main, post phases of a state
    def __init__(self, entity):
        self.entity = entity
        self.phases = {}
        self.current_phase = NullPhase(entity)

    def enter_phase(self, phase_name, **kwarg):#called when entering a new phase
        self.current_phase = self.phases[phase_name]
        self.current_phase.enter(**kwarg)

    def enter_state(self, phase_name, **kwarg):#called when entering a new state
        if not phase_name: phase_name = next(iter(self.phases))#get the first phase from the dictionary if not specified        
        self.common_values()
        self.enter_phase(phase_name, **kwarg) #enter the phase of the state

    def exit(self):#called when exiting the composite state
        self.current_phase.exit()

    def allowed(self):
        return True

    def common_values(self):#set common values for the phases
        pass

    def update(self, dt):
        self.current_phase.update(dt)

    def handle_input(self, input, **kwarg):
        self.current_phase.handle_input(input, **kwarg)

    def handle_press_input(self, input):
        self.current_phase.handle_press_input(input)

    def handle_release_input(self, input):
        self.current_phase.handle_release_input(input)

    def handle_movement(self, event):
        self.current_phase.handle_movement(event)

    def increase_phase(self):#called when an animation is finished for that state
        self.current_phase.increase_phase()   