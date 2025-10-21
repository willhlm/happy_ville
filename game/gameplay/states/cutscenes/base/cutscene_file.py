from engine.utils import read_files
from engine.system import animation

class CutsceneFile():#cutscneens that will run based on file. The name of the file should be the same as the class name
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.animation = animation.Animation(self)
        self.sprites = {'idle': read_files.load_sprites_list('cutscene/'+type(self).__name__.lower(), game_objects)}
        self.image = self.sprites['idle'][0]

    def update(self, dt):
        self.animation.update(dt)

    def render(self):
        self.game.render_display(self.image)  

    def reset_timer(self):#called when cutscene is finshed
        pass

    def handle_events(self,input):
        input.processed()