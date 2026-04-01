class DeathManager:
    def __init__(self, entity):
        self.entity = entity
        self.override = None

    def die(self):
        if self.entity.currentstate.composite_state is self.entity.currentstate.states['death']:
            return

        if self.override:
            self.override()
            return

        self.entity.currentstate.enter_state('death')
        self.entity.start_death_effects()

    def set_override(self, callback):
        self.override = callback

    def clear_override(self):
        self.override = None
