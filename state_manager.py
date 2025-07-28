import game_states
import game_states_facilities 
import game_states_cutscenes

class State_manager():
    def __init__(self, game, initial_state):
        self.game = game
        self.state_stack = [getattr(game_states, initial_state)(self.game)]  # Initialize with the first state
        self.category_map = {
            'game_states': game_states,
            'game_states_facilities': game_states_facilities,
            'game_states_cutscenes': game_states_cutscenes
        }

    def enter_state(self, state_name, category = 'game_states', **kwarg):
        """Push a new state onto the stack."""
        # Get the state class dynamically and instantiate it
        module = self.category_map[category]
        state = getattr(module, state_name)(self.game, **kwarg)
        self.state_stack.append(state)

    def exit_state(self):
        """Pop the current state off the stack."""
        state = self.state_stack.pop()
        state.on_exit()  # Call on_exit for the state we're exiting
        self.state_stack[-1].on_resume()  # Resume the previous state

    def update(self, dt):
        """Update the current active state."""
        self.state_stack[-1].update(dt)

    def render(self):
        """Render the current active state."""
        self.state_stack[-1].render()

    def handle_events(self, input):
        """Handle events in the current active state."""
        self.state_stack[-1].handle_events(input)
