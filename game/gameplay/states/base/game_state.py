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
        'called when exit'
        pass

    def on_resume(self):
        'called when popping the previous state'
        pass

    def on_pop(self):
        'called when popping'
        pass        

    def release_texture(self):#in the final version, this should not be needed sinec we wil not dynamically make layers
        pass
