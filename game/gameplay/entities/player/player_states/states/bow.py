from .base_composite import CompositeState
from .base_state import PhaseBase

class BowState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BowPre(entity), 'main': BowMain(entity)}

class BowPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self):
        self.entity.animation.play('bow_pre')
        self.duration = 100
        self.arrow = self.entity.game_objects.ui.hud.widgets.show_point_arrow(
            'bow',
            self.entity.rect.topleft,
            self.entity.dir.copy(),
        )
        self.time = 0

    def update(self, dt):
        self.duration -= dt
        self.time += dt
        self.entity.velocity = [0, 0]
        self.arrow.set_pos(self.entity.rect.topleft)
        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.entity.game_objects.ui.hud.widgets.hide('bow')
        self.enter_phase('main', dir = [self.arrow.dir[0], -self.arrow.dir[1]], time = self.time)

    def handle_release_input(self, input):
        if input.name == 'b':
            input.processed()
            self.exit_state()

    def handle_movement(self, axes):
        value = axes.move
        if value[0] != 0 or value[1] != 0:
            self.arrow.dir = [value[0], -value[1]]

class BowMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('bow_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Bow'].initiate(dir = kwarg['dir'], time = kwarg['time'])

    def increase_phase(self):
        self.enter_state('idle')
