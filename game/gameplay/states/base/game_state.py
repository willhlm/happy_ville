class GameState():
    def __init__(self,game):
        self.game = game

    def update(self, dt):
        pass

    def update_render(self, dt):
        pass

    def render(self):
        pass

    def handle_events(self, input):
        input.processed()

    def on_exit(self):
        'called when another state calls enter_state. This state is preserved.'
        pass

    def on_resume(self):
        'called when latest state calls exit_state, so that the previous state is resuming'
        pass

    def on_pop(self):
        'called when calling exit_state. This state is destroyed.'
        pass 

    def release_texture(self):
        pass
