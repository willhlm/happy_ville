from engine.system import animation

class CutsceneFile():#cutscneens that will run based on file. The name of the file should be the same as the class name
    def __init__(self, game):
        self.game = game
        self.animation = animation.Animation(self)

    def update(self, dt):
        self.animation.update(dt)

    def render(self):
        self.game.render_display(self.image)  

    def reset_timer(self):#called when cutscene is finshed
        pass

    def handle_events(self,input):
        input.processed()

    def update_render(self, dt):
        pass

    def on_exit(self):
        pass

    def fade_update(self, dt):
        pass