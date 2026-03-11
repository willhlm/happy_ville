from gameplay.states.base.game_state import GameState

class FadeIn(GameState):
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self.count = 0
        self.fade_length = kwargs.get("fade_length", 25)

        self.fade_surface = self.game.display.make_layer(self.game.window_size)
        self.fade_surface.clear(0, 0, 0, 255)        

    def update(self, dt):
        under_state = self.game.state_manager.peek_below_top()        
        under_state.update(dt)        
        self.count += dt
        if self.count > self.fade_length:
            self.exit()

    def update_render(self, dt):
        under_state = self.game.state_manager.peek_below_top()  
        under_state.update_render(dt)

    def exit(self):
        self.fade_surface.release()
        self.game.state_manager.exit_state()
        self.game.game_objects.signals.emit("fade_in_finished")

    def render(self):
        under_state = self.game.state_manager.peek_below_top()  
        under_state.render()

        alpha = max(int((self.fade_length - self.count) * (255 / self.fade_length)), 0)
        self.fade_surface.clear(0, 0, 0, alpha)
        self.game.render_display(self.fade_surface.texture)
