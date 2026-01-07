from engine.utils import read_files

class BackgroundMenu():#storea and renders the background for the menues
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/menus/title_menu/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/music/load_screen/')
        self.time = 0

        self.game_objects.shaders['title_screen']['resolution'] = self.game_objects.game.window_size     
        self.bg = self.sprites['start_screen'][0]   

    def update_time(self, dt):
        'the common background among menues'
        self.time += dt * 0.01
 
    def render_background(self, target):
        'the common background among menues'
        self.game_objects.ui.screen.clear(0,0,0,0)          

        self.game_objects.shaders['title_screen']['time'] = self.time
        self.game_objects.game.display.render(self.bg, target)
        self.game_objects.game.display.render(self.game_objects.ui.screen.texture, target, shader = self.game_objects.shaders['title_screen'])        