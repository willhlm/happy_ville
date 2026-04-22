class BaseUI:
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects

    def update(self, dt):
        self.letter_frame += dt
        self.screen_alpha += dt * 4
        self.screen_alpha = min(self.screen_alpha, 230)

    def render(self):
        pass

    def handle_events(self, input):
        input.processed()

    def on_exit(self, **kwarg):
        pass

    def on_enter(self, **kwarg):
        self.screen_alpha = kwarg.get('screen_alpha', 0)
        self.letter_frame = 0

    def exit_state(self):
        self.game_objects.game.state_manager.exit_state()

    def next_page(self, **kwarg):
        self.game_objects.ui.backpack.next_page(**kwarg)

    def previous_page(self, **kwarg):
        self.game_objects.ui.backpack.previous_page(**kwarg)

    def blit_screen(self):
        self.game_objects.shaders['alpha']['alpha'] = self.screen_alpha
        self.game_objects.game.display.render(
            self.game_objects.ui.backpack.screen.texture,
            self.game_objects.game.screen_manager.screen,
            shader=self.game_objects.shaders['alpha'],
        )
        self.game_objects.game.render_display(
            self.game_objects.game.screen_manager.screen.texture
        )
