from gameplay.states import Gameplay
from gameplay.ui.loaders import ItemPickupLoader


DYNAMIC_OVERLAY_LOADERS = {
    'item_pickup': ItemPickupLoader,
}

class DynamicOverlay(Gameplay):
    def __init__(self, game, loader_key, image, title='', text='', callback=None):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]
        self.fade = 0
        self.callback = callback
        self.should_exit = False
        self.overlay = game.display.make_layer(game.window_size)

        loader_cls = DYNAMIC_OVERLAY_LOADERS[loader_key]
        self.ui_loader = loader_cls(game.game_objects, image=image, title=title, text=text)
        self.game.game_objects.player.reset_movement()

    def on_pop(self):
        self.overlay.release()

    def update(self, dt):
        super().update(dt)
        if self.should_exit:
            if self.callback:
                self.callback()
            self.game.state_manager.exit_state()

    def handle_movement(self):
        pass

    def render(self):
        super().render()
        self.render_fade[self.page]()

        self.overlay.clear(0, 0, 0, 0)
        self.game.display.render(self.ui_loader.bg, self.overlay)
        self.render_images()
        self.render_text()
        self.render_buttons()
        self.game.game_objects.shaders['alpha']['alpha'] = self.fade
        self.game.display.render(self.overlay.texture, self.game.screen_manager.screen, shader=self.game.game_objects.shaders['alpha'])
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
        self.fade += 4
        self.fade = min(self.fade, 255)

    def render_out(self):
        self.fade -= 6
        self.fade = max(self.fade, 0)

        if self.fade == 0:
            self.should_exit = True

    def handle_events(self, input):
        input.processed()
        if input.pressed:
            if input.name == 'start':
                self.page = 1
            elif input.name == 'a':
                self.page = 1
