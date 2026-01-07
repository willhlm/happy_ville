from .states.composite_states import *

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
            #'dash_ground': DashGroundState(entity),
            #'dash_jump': DashJumpState(entity),
            #'wall_glide': WallGlideState(entity),
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
            #'dash_air': DashAirState(entity),
            'death': DeathState(entity),
            'respawn': ReSpawnState(entity),#used when respawning after death
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
        self._state_factories = {'dash_air': [('dash_air', DashAirState)],
                                'smash_up': [('smash_up', SmashUpState)],
                                'wall': [('wall_jump', WallJumpState), ('wall_glide', WallGlideState), ('belt_glide', BeltGlideState)],
                                'dash': [('dash_ground', DashGroundState), ('dash_jump', DashJumpState)],
                                'bow': [('bow', BowState)],
                                'thunder': [('thunder', ThunderState)],
                                'shield': [('shield', ShieldState)],
                                'wind': [('wind', WindState)],
                                'slow_motion': [('slow_motion', SlowMotionState)]}#should contain all the states that can be created, so that they can be be appended to self.stataes when needed

    def enter_state(self, state_name, phase = None, **kwargs):
        state = self.states.get(state_name)
        if state and state.allowed():#if the requested state is unlocked
            self.composite_state.exit()#exit the old one before entering/setting a new state
            state.enter_state(phase, **kwargs)
            self.composite_state = state

    def update(self, dt):#called from player
        self.composite_state.update(dt)#main state

    def handle_input(self, input, **kwargs):
        self.composite_state.handle_input(input, **kwargs)

    def handle_press_input(self, input):
        self.composite_state.handle_press_input(input)

    def handle_release_input(self, input):
        self.composite_state.handle_release_input(input)

    def handle_movement(self, event):#called from gameplay loop state
        self.composite_state.handle_movement(event)

    def increase_phase(self):#called when an animation is finished for that state
        self.composite_state.increase_phase()

    def unlock_state(self, name):#should be called when unlocking a new state
        for state_name, cls in self._state_factories[name]:
            self.states[state_name] = cls(self.entity)
