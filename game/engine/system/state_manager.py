from gameplay.states import *

class State_manager():
    def __init__(self, game, initial_state = 'title_menu'):
        self.game = game
        self.state_stack = [self._build_state(initial_state)]  # Initialize with the first state

    def _build_state(self, state_name, **kwarg):
        state = REGISTERY[state_name](self.game, **kwarg)
        state.state_name = state_name
        return state

    def enter_state(self, state_name, **kwarg):
        """Push a new state onto the stack."""
        state = self._build_state(state_name, **kwarg)
        self.state_stack[-1].on_exit()
        self.state_stack.append(state)        

    def exit_state(self):
        """Pop the current state off the stack."""
        state = self.state_stack.pop()
        state.on_pop()  # Call on_exit for the state we're exiting
        self.state_stack[-1].on_resume()  # Resume the previous state

    def exit_to_state(self, state_name):
        while len(self.state_stack) > 1 and self.state_stack[-1].state_name != state_name:
            state = self.state_stack.pop()
            state.on_pop()

        if self.state_stack[-1].state_name == state_name:
            self.state_stack[-1].on_resume()

    def update(self, dt):
        """Update the current active state."""
        self.state_stack[-1].update(dt)

    def update_render(self, dt):
        """Update the current active state."""
        self.state_stack[-1].update_render(dt)

    def render(self):
        """Render the current active state."""
        self.state_stack[-1].render()

    def handle_events(self, input):
        """Handle events in the current active state."""
        self.state_stack[-1].handle_events(input)

    def peek_below_top(self):
        'return the state just below the current one'
        return self.state_stack[-2]

    def has_state(self, state_name):
        return state_name in REGISTERY

REGISTERY = {
    # Menus
    "load_menu": LoadMenu,
    "option_display": OptionDisplay,
    "option_sounds": OptionSounds,
    "option_menu": OptionMenu,
    "pause_menu": PauseMenu,
    "title_menu": TitleMenu,

    #overlays
    "static_overlay": StaticOverlay,
    "dynamic_overlay": DynamicOverlay,

    # Gameplay
    "gameplay": WorldGameplay,
    "ability_select": AbilitySelect,
    "blit_image_text": BlitImageText,
    "conversation": Conversation,
    "screen_fade": ScreenFadeState,
    "backpack_ui": BackpackUIState,

    # Facilities
    "bank_deposite": BankDeposite,
    "bank_widthdraw": BankWidthdraw,
    "bank": Bank,
    "fast_travel_menu": FastTravelMenu,
    "fast_travel_unlock": FastTravelUnlock,
    "smith": Smith,
    "soul_essence": SoulEssence,
    "vendor_2": Vendor_2,
    "vendor": Vendor,
    'weaver': Weaver,

    # Cutscenes
    "rhoutta_encounter_defeat": RhouttaEncounterDefeat,
    "new_game": NewGame,
}
