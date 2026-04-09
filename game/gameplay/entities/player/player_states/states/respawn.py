from .base_composite import CompositeState
from .base_state import PhaseBase

class ReSpawnState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': ReSpawnMain(entity)}

class ReSpawnMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('respawn')
        self.entity.invincibile = False

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.entity.vitals.set_health(max(self.entity.vitals.health, 0))
        self.entity.heal_vitals(self.entity.vitals.max_health)
        if self.entity.backpack.map.spawn_point.get('bone', False):
            self.entity.backpack.map.spawn_point.pop()
        self.enter_state('idle')
