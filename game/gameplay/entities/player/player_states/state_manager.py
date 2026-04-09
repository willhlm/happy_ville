from .states import *


class StateManager():
    def __init__(self, entity):
        self.entity = entity
        self.states = {
            'idle': IdleState(entity),
            'invisible': InvisibleState(entity),
            'run': RunState(entity),
            'walk': WalkState(entity),
            'sprint': SprintState(entity),
            'fall': FallState(entity),
            'land': LandState(entity),
            'jump': JumpState(entity),
            'jump_sprint': JumpSprintState(entity),
            'dash_ground': DashGroundState(entity),
            'dash_jump': DashJumpState(entity),
            'wall_glide': WallGlideState(entity),
            'belt_glide': BeltGlideState(entity),
            'wall_jump': WallJumpState(entity),
            'sword_stand1': SwordStand1State(entity),
            'sword_stand2': SwordStand2State(entity),
            'sword_air1': SwordAir1State(entity),
            'sword_air2': SwordAir2State(entity),
            'sword_down': SwordDownState(entity),
            'sword_up': SwordUpState(entity),
            'smash_side': SmashSideState(entity),
            'smash_up': SmashUpState(entity),
            'dash_air': DashAirState(entity),
            'death': DeathState(entity),
            'respawn': ReSpawnState(entity),
            'heal': HealState(entity),
            'crouch': CrouchState(entity),
            'plat_bone': PlantBoneState(entity),
            'thunder': ThunderState(entity),
            'shield': ShieldState(entity),
            'wind': WindState(entity),
            'slow_motion': SlowMotionState(entity),
            'bow': BowState(entity),
        }

        self.composite_state = self.states['idle']
        self.composite_state.enter_phase('main')

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

    def increase_phase(self):
        self.composite_state.increase_phase()
