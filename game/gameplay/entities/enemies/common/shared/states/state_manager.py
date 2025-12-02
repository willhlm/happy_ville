from gameplay.entities.enemies.common.shared.cooldown_manager import CooldownManager
from gameplay.entities.enemies.common.shared.states import SHARED_STATES
from gameplay.entities.enemies.common.shared.deciders import SHARED_DECIDERS

class StateManager:
    def __init__(self, entity, type = 'ground', custom_states = {}, custom_deciders = None, universal_states = ['death', 'hurt', 'attack_pre', 'attack_main', 'wait']):
        self.entity = entity
        self.cooldowns = CooldownManager()
        self.player_distance = [0, 0]
        
        all_states = {**SHARED_STATES[type], **(custom_states or {})}
        self.deciders = {**SHARED_DECIDERS, **(custom_deciders or {})}
        
        # Load only configured, consom_states + universal states
        self.states = {}               
        all_state_names = set(list(entity.config['states'].keys()) + universal_states + list(custom_states.keys()))# Combine all state names (remove duplicates with set)
        for state in all_state_names:            
            self.states[state] = all_states[state]            

        initial_state = entity.config.get('initial_state', 'patrol')
        self.enter_state(initial_state)
    
    def enter_state(self, state_name, **kwargs):
        if self.states.get(state_name.lower(), False):
            self.state  = self.states[state_name.lower()](self.entity, self.deciders, config_key = state_name.lower(), **kwargs)

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
        self.player_distance = [player.hitbox.centerx - self.entity.hitbox.centerx, player.hitbox.centery - self.entity.hitbox.centery]