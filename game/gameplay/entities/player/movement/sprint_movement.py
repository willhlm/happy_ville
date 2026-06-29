class SprintMovement:
    def __init__(self, entity):
        self.entity = entity
        self.chain_requested = False

    def reset(self):
        self.clear_chain()

    def can_sprint(self):
        return self.entity.currentstate.has_state('sprint')

    def request_chain(self):
        self.chain_requested = self.can_sprint()

    def clear_chain(self):
        self.chain_requested = False

    def should_chain(self):
        return (
            self.chain_requested
            and self.can_sprint()
            and self.entity.game_objects.controller.is_held('lb')
        )
