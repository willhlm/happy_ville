from gameplay.states import Gameplay

class SafeSpawn_2(Gameplay):#fade
    def __init__(self, game):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.count = 0
        self.fade_length = 20
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)
        self.game.game_objects.player.set_pos(self.game.game_objects.player.backpack.map.spawn_point['safe_spawn'])
        self.game.game_objects.player.currentstate.enter_state('crouch', phase = 'main')

    def update(self, dt):
        super().update(dt)
        self.count += dt
        if self.count > self.fade_length*2:
            self.game.game_objects.player.currentstate.handle_input('pray_post')
            self.game.state_manager.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.render_display(self.fade_surface.texture)

