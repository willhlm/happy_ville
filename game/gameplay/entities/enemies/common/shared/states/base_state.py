import random

class BaseState():
    def __init__(self, entity, deciders, config_key):
        self.entity = entity
        self.config_key = config_key#name of the state in config file
        self.deciders = []
        self._load_deciders(deciders)

    def _load_deciders(self, deciders):
        state_config = self.entity.config['states'].get(self.config_key, {})
        decider_configs = state_config.get('deciders', {})        
        
        for decider_name, kwargs in decider_configs.items():
            decider_class = deciders[decider_name]   
            self.deciders.append(decider_class(self.entity, **kwargs))

    def update(self, dt):
        self.update_logic(dt)
        self.check_transitions(dt)

    def update_logic(self, dt):
        """Override in subclasses: movement, attack, etc."""
        pass

    def check_transitions(self, dt):
        """
        Evaluate all deciders attached to this state and determine whether the enemy should transition into another state.

        Process:
        1. Ask each decider for a list of possible decisions (with score/priority).
        2. Collect all candidate decisions into a single list.
        3. Find the highest priority among all candidates.
        - This ensures that "safety" or "critical" decisions (like no ground) always override less important ones (like choosing an attack).
        4. From the candidates in that priority tier, pick one using weighted randomness based on their score.
        - Higher score → higher probability of being chosen.
        5. If a best decision is found, exit the current state and enter the new one with any parameters provided.

        Example:
            - EdgeDecider returns "wait" (priority 10, score 90).
            - AttackDecider returns "jump_attack_pre" (priority 5, score 80).
            => "wait" will be chosen, since it has higher priority.
        """        
        candidates = []
        for decider in self.deciders:
            results = decider.choose(self.player_distance, dt)
            if results:
                candidates.extend(results)

        if not candidates: return  # stay in current state            

        # --- select the highest priority tier ---
        max_priority = max(d.priority for d in candidates)
        filtered = [d for d in candidates if d.priority == max_priority]

        # Weighted random choice within that tier
        states = [d for d in filtered]
        weights = [d.score for d in filtered]
        best = random.choices(states, weights=weights, k=1)[0]

        self.enter_state(best.next_state, **best.kwargs)

    def enter_state(self, state_name, **kwargs):
        self.entity.currentstate.enter_state(state_name, **kwargs)

    def handle_input(self, input_type):
        if input_type == "Hurt" and self.entity.flags.get("hurt_state_able", True):
            self.enter_state("hurt")

    def modify_hit(self, effect):
        return effect

    def increase_phase(self):
        """Called when animation phase completes"""
        pass

    @property
    def player_distance(self):
        # Fetch from manager instead of storing locally
        return self.entity.currentstate.player_distance
