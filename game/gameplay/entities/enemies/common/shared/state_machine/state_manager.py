from gameplay.entities.enemies.common.shared.state_machine.cooldown_manager import CooldownManager
from gameplay.entities.enemies.common.shared.state_machine.states import SHARED_STATES
from gameplay.entities.enemies.common.shared.state_machine.deciders import SHARED_DECIDERS


class StateManager:
    def __init__(self, entity, type='ground', custom_states={}, custom_deciders=None, universal_states=['death', 'dead', 'hurt', 'wait']):
        self.entity = entity
        self.cooldowns = CooldownManager()
        self.player_distance = [0, 0]

        all_states = {**SHARED_STATES[type], **(custom_states or {})}
        self.deciders = {**SHARED_DECIDERS, **(custom_deciders or {})}

        # Load only states explicitly configured/referenced for this enemy plus declared custom/universal states.
        self.states = {}
        all_state_names = self._collect_state_names(entity, universal_states, custom_states)
        for state in all_state_names:
            if state in all_states:
                self.states[state] = all_states[state]

        initial_state = entity.config.get('initial_state', 'patrol')
        self.enter_state(initial_state)

    def _collect_state_names(self, entity, universal_states, custom_states):
        state_names = set(entity.config.get('states', {}).keys())
        state_names.update(universal_states)
        state_names.update((custom_states or {}).keys())
        state_names.add(entity.config.get('initial_state', 'patrol'))

        return state_names

    def enter_state(self, state_name, **kwargs):
        normalized_state = state_name.lower()
        if self.states.get(normalized_state, False):
            self.state = self.states[normalized_state](self.entity, self.deciders, config_key=normalized_state, **kwargs)

    def update(self, dt):
        """Update cooldowns and current state"""
        self.cooldowns.update(dt)
        self.check_player_distance()
        self.state.update(dt)

    def consume_contact_state(self):
        self.state.consume_contact_state()

    def handle_input(self, input_type):
        """Pass input to current state"""
        self.state.handle_input(input_type)

    def increase_phase(self):
        """Progress to next phase of current state"""
        self.state.increase_phase()

    def check_player_distance(self):
        player = self.entity.game_objects.player
        self.player_distance = [player.hitbox.centerx - self.entity.hitbox.centerx, player.hitbox.centery - self.entity.hitbox.centery]

    def die(self):
        death_state = self.states.get('death')
        dead_state = self.states.get('dead')
        if death_state and isinstance(self.state, death_state):  # if already in death flow
            return
        if dead_state and isinstance(self.state, dead_state):
            return
        self.entity.killed()
        self.enter_state("death")
