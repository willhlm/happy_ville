from .sequences import HeavenIntro

class WorldTransformController:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.active_sequence = NullSequence()
        self.registery = {'heaven_intro': HeavenIntro}

    def start(self, transform_id, source_pos):
        self.active_sequence = self.registery[transform_id](self.game_objects, source_pos)

    def update_render(self, dt):
        self.active_sequence.update_render(dt)

    def deactivate(self):
        self.active_sequence = NullSequence()

class NullSequence():
    def __init__(self):
        pass

    def update_render(self, dt):
        pass

