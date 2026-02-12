from gameplay.states.base.game_state import GameState

class FadeOut(GameState):
    def __init__(self, game, previous_state, **kwargs):
        super().__init__(game)
        self.previous_state = previous_state        
        self.fade_length = kwargs.get("fade_length", 25)
        self.count = 0
        
        self.fade_surface = self.game.display.make_layer(self.game.window_size)                
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))

    def update(self, dt):
        self.previous_state.update(dt)
        self.count += dt
        if self.count > self.fade_length:
            self.exit()

    def update_render(self, dt):
        self.previous_state.update_render(dt)

    def exit(self):
        self.fade_surface.release()
        self.game.state_manager.exit_state()#has to be before loadmap
        self.game.game_objects.signals.emit('fade_covered')

    def render(self):
        self.previous_state.render()#to make ti continue rendering even whenfading
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.render_display(self.fade_surface.texture)

