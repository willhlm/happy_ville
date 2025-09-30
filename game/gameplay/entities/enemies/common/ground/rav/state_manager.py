from .rav_states import *
from gameplay.entities.shared.cooldown_manager import CooldownManager
from .attack_decider import AttackDecider

class RavStateManager:
    def __init__(self, entity):
        self.entity = entity
        self.cooldowns = CooldownManager()
        self.attack_decider = AttackDecider(self)
        
        self.states = {
            'idle': Idle,
            'patrol': Patrol,
            'wait': Wait,
            'chase': Chase,
            'attack_pre': AttackPre,
            'attack_main': AttackMain,
            'jump_attack_pre': JumpAttackPre,
            'jump_attack_main': JumpAttackMain,
            'jump_attack_post': JumpAttackPost,
            'hurt': Hurt,
            'jump_back': JumpBack,
            'death': Death,
        }

        # Start in patrol state
        self.enter_state('patrol')

    def enter_state(self, state_name, **kwargs):                
        self.state = self.states[state_name](self.entity, **kwargs)

    def update(self, dt):
        """Update cooldowns and current state"""
        self.cooldowns.update(dt)
        self.state.update(dt)

    def handle_input(self, input_type):
        """Pass input to current state"""
        self.state.handle_input(input_type)

    def increase_phase(self):
        """Progress to next phase of current state"""
        self.state.increase_phase()