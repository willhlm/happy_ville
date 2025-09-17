from engine.utils import read_files
from gameplay.states import FadeIn

class FadeOut(FadeIn):
    def __init__(self,game, previous_state, map_name, spawn, fade):
        super().__init__(game)
        self.previous_state = previous_state
        self.fade_length = 25
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))
        self.map_name = map_name
        self.spawn = spawn
        self.fade = fade

    def init(self):
        pass

    def update_render(self, dt):
        self.previous_state.fade_update(dt)#so that it don't consider player input
        self.count += dt
        if self.count > self.fade_length:
            self.exit()

    def exit(self):
        self.fade_surface.release()
        self.game.state_manager.exit_state()#has to be before loadmap
        self.game.game_objects.load_map2(self.map_name, self.spawn, self.fade)

    def render(self):
        self.previous_state.render()
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.render_display(self.fade_surface.texture)

