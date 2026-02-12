from gameplay.states import *

class State_manager():
    def __init__(self, game, initial_state = 'title_menu'):
        self.game = game
        self.state_stack = [REGISTERY[initial_state](self.game)]  # Initialize with the first state

    def enter_state(self, state_name, **kwarg):
        """Push a new state onto the stack."""
        # Get the state class dynamically and instantiate it
        state = REGISTERY[state_name](self.game, **kwarg)        
        self.state_stack.append(state)        

    def exit_state(self):
        """Pop the current state off the stack."""
        state = self.state_stack.pop()
        state.on_exit()  # Call on_exit for the state we're exiting
        self.state_stack[-1].on_resume()  # Resume the previous state

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

REGISTERY = {
    # Menus
    "load_menu": LoadMenu,
    "option_display": OptionDisplay,
    "option_sounds": OptionSounds,
    "option_menu": OptionMenu,
    "pause_menu": PauseMenu,
    "title_menu": TitleMenu,

    #overlays
    "instructions": Instructions,

    # Gameplay
    "gameplay": Gameplay,
    "ability_select": AbilitySelect,
    "blit_image_text": BlitImageText,
    "conversation": Conversation,
    "fade_in": FadeIn,
    "fade_out": FadeOut,
    "safe_spawn_1": SafeSpawn_1,
    "safe_spawn_2": SafeSpawn_2,
    "uis": UIs,

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

    # Cutscenes
    "boss_deer_encounter": BossDeerEncounter,
    "tutorial_boss_encounter": TutorialBossEncounter,
    "butterfly_encounter": ButterflyEncounter,
    "cultist_encounter": CultistEncounter,
    "death": Death,
    "deer_encounter": DeerEncounter,
    "defeated_boss": DefeatedBoss,
    "start_game": StartGame,
    "rhoutta_encounter_defeat": RhouttaEncounterDefeat,
    "title_screen": TitleScreen,
    "new_game": NewGame,
}