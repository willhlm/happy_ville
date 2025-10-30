from gameplay.states import Gameplay

class FadeIn(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.count = 0
        self.fade_length = 25
        self.init()
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)

    def init(self):
        self.aila_state = 'Idle_main'#for respawn after death
        for state in self.game.state_manager.state_stack:
            if 'Death' == type(state).__name__:
                self.aila_state = 'Invisible_main'
                self.game.game_objects.player.currentstate.enter_state('Invisible_main')
                break

    def update_render(self, dt):
        self.fade_update(dt)#so that it doesn't collide with collision path
        self.count += dt
        if self.count > self.fade_length*2:
            self.exit()

    def exit(self):
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.currentstate.enter_state(self.aila_state)
        self.fade_surface.release()
        self.game.state_manager.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.render_display(self.fade_surface.texture)

