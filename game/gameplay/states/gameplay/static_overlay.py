from gameplay.states import Gameplay
from gameplay.ui.loaders import DashInstructionLoader

OVERLAY_LOADERS = {
    'dash': DashInstructionLoader,
}

class StaticOverlay(Gameplay):#when player obtaines a new ability, pick up inetractable item etc. It blits an image and text
    def __init__(self, game, overlay_key, callback=None):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]
        self.fade = self.game.game_objects.fade.create("alpha", 0, max_value=150)
        self.should_exit = False
        self.callback = callback
        self.overlay = game.display.make_layer(game.window_size)

        loader_cls = OVERLAY_LOADERS[overlay_key]
        self.ui_loader = loader_cls(game.game_objects)
        self.game.game_objects.player.reset_movement()        

    def on_pop(self):
        self.overlay.release()

    def update(self, dt):
        super().update(dt)
        if self.should_exit:
            if self.callback:
                self.callback()
            self.game.state_manager.exit_state()

    def handle_movement(self):#every frame
        pass

    def render(self):
        super().render()
        self.render_fade[self.page]()

        self.overlay.clear(0, 0, 0, 0)
        self.game.display.render(self.ui_loader.bg, self.overlay)
        self.render_images()
        self.render_text()
        self.render_buttons()
        self.fade.render(
            self.overlay.texture,
            self.game.screen_manager.screen,
        )

        self.game.render_display(self.game.screen_manager.screen.texture)

    def render_images(self):
        for image in self.ui_loader.images:
            image.render(self.overlay)

    def render_text(self):
        for text in self.ui_loader.texts:
            text.render(self.overlay)

    def render_buttons(self):
        for button in self.ui_loader.buttons.values():
            button.render(self.overlay)

    def render_in(self):
        self.fade.step(2)

    def render_out(self):
        self.fade.step(-4)

        if self.fade.value <= 0:
            self.should_exit = True

    def handle_events(self,input):
        input.processed()
        if input.pressed:#press
            if input.name == 'start':
                self.page = 1
            elif input.name == 'a':
                self.page = 1
