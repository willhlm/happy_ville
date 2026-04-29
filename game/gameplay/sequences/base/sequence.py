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
