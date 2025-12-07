from .base_composite import CompositeState
from .states import *

#wrappers
class FallState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': FallPre(entity), 'main': FallMain(entity)}

    def enter_state(self, phase_name, **kwarg):
        super().enter_state(phase_name, **kwarg)
        self.allow_sprint = kwarg.get('allow_sprint', False)

    def common_values(self):#call when this state is enetred
        self.falltime = 0

    def update(self, dt):
        self.falltime += dt

    def determine_fall(self):
        if self.falltime >= 4000: return True
        return False

    def determine_sprint(self):
        return self.allow_sprint

class LandState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'soft': LandSoftMain(entity), 'hard': LandHardMain(entity)}

class InvisibleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': Invisible(entity)}

class RunState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': RunPre(entity), 'main': RunMain(entity), 'post': RunPost(entity)}

class WalkState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': WalkPre(entity), 'main': WalkMain(entity), 'post': WalkPost(entity)}

class SprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SprintMain(entity), 'post': SprintPost(entity)}#'pre': SprintPre(entity),

class IdleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': IdleMain(entity)}

class JumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': JumpMain(entity)}

class JumpSprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': JumpSprintPre(entity),'main': JumpSprintMain(entity),'post': JumpSprintPost(entity)}

class DashGroundState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashGroundPre(entity), 'main': DashGroundMain(entity), 'post': DashGroundPost(entity)}

    def common_values(self):#called when entering this new state, and will not change during phase changes
        self.dir = self.entity.dir.copy()#copy the direction of the entity, and save it in the state across phases

    def allowed(self):
        return self.entity.flags['grounddash']

class WallGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallGlide(entity, animation_name = 'wall_glide_main')}#{'pre': WallGlide(entity, animation_name = 'wall_glide_pre'), 'main': WallGlide(entity, animation_name = 'wall_glide_main')}

class BeltGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BeltGlide(entity, animation_name = 'wall_glide_pre'), 'main': BeltGlide(entity, animation_name = 'wall_glide_main')}

class DashJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashJumpPre(entity)}#, 'main': DashJumpMain(entity), 'post': DashJumpPost(entity)}

    def allowed(self):
        return self.entity.flags['grounddash']

class WallJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallJumpMain(entity)}#'pre': WallJumpPre(entity),

class SwordStand1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {#'pre': SwordStandPre(entity, animation_name = 'sword_stand1_pre'),
                       'main': SwordStandMain(entity, animation_name = 'sword_stand1_main'),
                       'post': SwordStandPost(entity, animation_name = 'sword_stand1_post')}#

class SwordStand2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {#'pre': SwordStandPre(entity, animation_name = 'sword_stand2_pre'),
                       'main': SwordStandMain(entity, animation_name = 'sword_stand2_main'),
                       'post': SwordStandPost(entity, animation_name = 'sword_stand2_post')}#

class SwordDownState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordDownMain(entity)}

class SwordUpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordUpMain(entity)}

class SmashSideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SmashSidePre(entity), 'charge': SmashSideCharge(entity), 'main': SmashSideMain(entity), 'post': SmashSidePost(entity)}

class SmashUpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SmashUpPre(entity), 'charge': SmashUpCharge(entity), 'main': SmashUpMain(entity), 'post': SmashUpPost(entity)}

class SwordAir1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air1_main')}

class SwordAir2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air2_main')}

class DashAirState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashAirPre(entity), 'main': DashAirMain(entity), 'post': DashAirPost(entity)}

class DeathState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DeathPre(entity), 'main': DeathMain(entity), 'post': DeathPost(entity)}

class ReSpawnState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': ReSpawnMain(entity)}

class HealState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': HealPre(entity), 'main': HealMain(entity)}

class CrouchState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': CrouchPre(entity), 'main': CrouchMain(entity), 'post': CrouchPost(entity)}

class PlantBoneState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': PlantBoneMain(entity)}

class ThunderState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': ThunderPre(entity), 'main': ThunderMain(entity), 'post': ThunderPost(entity)}

class ShieldState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': ShieldPre(entity), 'main': ShieldMain(entity)}

class WindState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WindMain(entity)}

class SlowMotionState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SlowMotionPre(entity), 'main': SlowMotionMain(entity)}

class BowState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BowPre(entity), 'main': BowMain(entity)}