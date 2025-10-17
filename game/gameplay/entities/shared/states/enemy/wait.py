from .base_state import BaseState

class Wait(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("idle", 0.2)
        
        # Store wait parameters for decider
        self.dir = kwargs.get('dir', 1)        
        self.wait_time = kwargs.get('time', 50)
        self.next_state = kwargs.get('next_state', 'patrol')    

    def handle_input(self, input_type):
        if input_type == "Hurt":
            self.enter_state("chase")   