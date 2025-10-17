from gameplay.entities.shared.cooldown_manager import CooldownManager
from gameplay.entities.shared.states import SHARED_STATES
from gameplay.entities.shared.deciders import SHARED_DECIDERS

class StateManager:
    def __init__(self, entity, custom_states = None, custom_deciders = None):
        self.entity = entity
        self.cooldowns = CooldownManager()
        self.player_distance = [0, 0]

        self.states = {**SHARED_STATES, **(custom_states or {})}#merge and overwrite if overlap
        self.deciders = {**SHARED_DECIDERS, **(custom_deciders or {})}#merge and overwrite if overlap

        # Start in patrol state
        initial_state = entity.config.get('initial_state', 'patrol')
        self.enter_state(initial_state)

    def enter_state(self, state_name, **kwargs):                        
        self.state = self.states[state_name.lower()](self.entity, self.deciders, **kwargs)

    def update(self, dt):
        """Update cooldowns and current state"""
        self.cooldowns.update(dt)
        self.check_player_distance()
        self.state.update(dt)

    def handle_input(self, input_type):
        """Pass input to current state"""
        self.state.handle_input(input_type)

    def increase_phase(self):
        """Progress to next phase of current state"""
        self.state.increase_phase()

    def modify_hit(self, effect):
        effect = self.state.modify_hit(effect)
        return effect

    def check_player_distance(self):
        player = self.entity.game_objects.player
        self.player_distance = [player.rect.centerx - self.entity.rect.centerx, player.rect.centery - self.entity.rect.centery]