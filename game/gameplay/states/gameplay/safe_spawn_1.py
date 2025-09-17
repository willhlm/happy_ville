from gameplay.states import Gameplay

class SafeSpawn_1(Gameplay):#basically fade. Uses it when collising a hole
    def __init__(self, game):
        super().__init__(game)
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.count = 0
        self.fade_length = 60
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))

    def update(self, dt):
        super().update(dt)
        self.count += dt
        if self.count > self.fade_length:
            self.game.state_manager.exit_state()
            self.game.state_manager.enter_state('Safe_spawn_2')

    def render(self):
        super().render()#gameplay render
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.render_display(self.fade_surface.texture)

