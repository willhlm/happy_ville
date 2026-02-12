class StateManager:
    """Manages particle state transitions in a type-safe manner."""
    
    def __init__(self, particle, initial_state_class):
        """
        Initialize state manager.
        
        Args:
            particle: The particle entity this manager controls
            initial_state_class: Class (not instance) of the initial state
        """
        self.particle = particle
        self.current_state = initial_state_class(particle)
    
    def transition_to(self, state_class, **kwargs):
        """
        Transition to a new state.
        
        Args:
            state_class: The class of the new state to transition to
            **kwargs: Additional parameters to pass to state constructor
        """
        self.current_state = state_class(self.particle, **kwargs)
    
    def update(self, dt):
        """Update the current state."""
        self.current_state.update(dt)
    
    def update_render(self, dt):
        """Update and render the current state."""
        self.current_state.update_render(dt)
