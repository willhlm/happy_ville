from .base_composite import CompositeState
from .base_state import PhaseBase

class PlantBoneState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': PlantBoneMain(entity)}

class PlantBoneMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('plant_bone_main')
        self.entity.acceleration[0] = 0

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_state('idle')


