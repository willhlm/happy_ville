from .states import *


class StateManager():
    BASE_STATE_KEYS = (
        'idle',
        'invisible',
        'run',
        'walk',
        'fall',
        'land',
        'jump',
        'sword_stand1',
        'sword_stand2',
        'sword_air1',
        'sword_air2',
        'sword_down',
        'sword_up',
        'smash_side',
        'smash_up',
        'death',
        'respawn',
        'heal',
        'crouch',
        'plat_bone',
        'pray',
    )

    def __init__(self, entity):
        self.entity = entity
        self._state_factories = {
            'idle': IdleState,
            'invisible': InvisibleState,
            'run': RunState,
            'walk': WalkState,
            'sprint': SprintState,
            'fall': FallState,
            'land': LandState,
            'jump': JumpState,
            'jump_sprint': JumpSprintState,
            'dash_ground': DashGroundState,
            'dash_jump': DashJumpState,
            'wall_glide': WallGlideState,
            'wall_jump': WallJumpState,
            'sword_stand1': SwordStand1State,
            'sword_stand2': SwordStand2State,
            'sword_air1': SwordAir1State,
            'sword_air2': SwordAir2State,
            'sword_down': SwordDownState,
            'sword_up': SwordUpState,
            'smash_side': SmashSideState,
            'smash_up': SmashUpState,
            'dash_air': DashAirState,
            'air_glide': AirGlideState,
            'death': DeathState,
            'respawn': ReSpawnState,
            'heal': HealState,
            'crouch': CrouchState,
            'plat_bone': PlantBoneState,
            'thunder': ThunderState,
            'shield': ShieldState,
            'wind': WindState,
            'slow_motion': SlowMotionState,
            'bow': BowState,
            'pray': PrayState,
        }
        self.states = {}
        self.install_states(self.BASE_STATE_KEYS)

        self.composite_state = self.states['idle']
        self.composite_state.enter_phase('main')

    def install_state(self, state_name):
        if state_name not in self.states:
            self.states[state_name] = self._state_factories[state_name](self.entity)

    def install_states(self, state_names):
        for state_name in state_names:
            self.install_state(state_name)

    def has_state(self, state_name):
        return state_name in self.states

    def is_in_state(self, state_name):
        return self.states.get(state_name) is self.composite_state

    def enter_state(self, state_name, phase=None, **kwargs):
        state = self.states.get(state_name)
        if state and state.allowed():
            self.composite_state.exit()
            state.enter_state(phase, **kwargs)
            self.composite_state = state

    def update(self, dt):
        self.composite_state.update(dt)

    def consume_contact_state(self):
        self.composite_state.consume_contact_state()

    def handle_input(self, input, **kwargs):
        self.composite_state.handle_input(input, **kwargs)

    def handle_press_input(self, input):
        self.composite_state.handle_press_input(input)

    def handle_release_input(self, input):
        self.composite_state.handle_release_input(input)

    def handle_movement(self, event):
        self.composite_state.handle_movement(event)

    def can_interact(self):
        return self.composite_state.can_interact()

    def get_move_dir_x(self):
        return self.composite_state.get_move_dir_x()

    def increase_phase(self):
        self.composite_state.increase_phase()
