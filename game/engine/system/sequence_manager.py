class SequenceManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.sequences = {}

    def start_sequence(self, key, **kwargs):
        if key in self.sequences:
            return self.sequences[key]

        sequence_cls = self.game_objects.registry.fetch('sequences', key)
        if sequence_cls is None:
            raise KeyError(f"Unknown sequence: {key}")

        sequence = sequence_cls(self.game_objects, manager=self, key=key, **kwargs)
        self.sequences[key] = sequence
        return sequence

    def stop_sequence(self, key):
        sequence = self.sequences.pop(key, None)
        if sequence:
            sequence.cleanup()

    def is_active(self, key):
        return key in self.sequences

    def blocks_gameplay_input(self):
        return any(sequence.blocks_gameplay_input for sequence in self.sequences.values())

    def blocks_gameplay_movement(self):
        return any(sequence.blocks_gameplay_movement for sequence in self.sequences.values())

    def update(self, dt):
        for sequence in list(self.sequences.values()):
            sequence.update(dt)

    def update_render(self, dt):
        for sequence in list(self.sequences.values()):
            sequence.update_render(dt)

    def render(self, target):
        for sequence in list(self.sequences.values()):
            sequence.render(target)

    def draw(self, composite_target):
        if not self.sequences:
            return

        screen = self.game_objects.game.screen_manager.screen
        screen.clear(0, 0, 0, 0)
        self.render(screen)
        self.game_objects.game.display.render(screen.texture, composite_target, scale=self.game_objects.game.scale)

class Sequence:
    blocks_gameplay_input = False
    blocks_gameplay_movement = False

    def __init__(self, game_objects, manager, key):
        self.game_objects = game_objects
        self.manager = manager
        self.key = key

    def update(self, dt):
        pass

    def update_render(self, dt):
        pass

    def finish(self):
        self.manager.stop_sequence(self.key)

    def cleanup(self):
        pass

    def render(self, target):
        pass
