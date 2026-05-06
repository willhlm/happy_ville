from gameplay.states.base.game_state import GameState


class ScreenFadeState(GameState):
    def __init__(self, game, *, fade_length=25, initial_alpha=0, target_alpha=255, under_state=None, style="alpha", colour=(0, 0, 0, 255), signal_name=None, **fade_kwargs):
        super().__init__(game)
        self.fade_length = max(float(fade_length), 1.0)
        self.initial_alpha = float(initial_alpha)
        self.target_alpha = float(target_alpha)
        self.under_state = under_state
        self.style = style
        self.signal_name = signal_name
        self.count = 0.0
        self.fade_kwargs = dict(fade_kwargs)

        self.fade = self.game.game_objects.fade.create(
            style,
            initial_alpha,
            min_value=min(self.initial_alpha, self.target_alpha),
            max_value=max(self.initial_alpha, self.target_alpha),
        )

        self.fade_surface = self.game.display.make_layer(self.game.window_size)
        self.fade_surface.clear(*colour)

    def update(self, dt):
        self._active_under_state().update(dt)
        self.count += dt
        progress = min(self.count / self.fade_length, 1.0)
        alpha = self.initial_alpha + (self.target_alpha - self.initial_alpha) * progress
        self.fade.set(alpha)
        if progress >= 1.0:
            self.exit()

    def update_render(self, dt):
        self._active_under_state().update_render(dt)

    def render(self):
        self._active_under_state().render()
        self.fade.render(
            self.fade_surface.texture,
            self.game.display.screen,
            scale=self.game.scale,
        )

    def exit(self):
        self.game.state_manager.exit_state()
        self._emit_signal()

    def on_pop(self):
        self.fade_surface.release()

    def _emit_signal(self):
        if self.signal_name:
            self.game.game_objects.signals.emit(self.signal_name)

    def _active_under_state(self):
        if self.under_state is not None:
            return self.under_state
        return self.game.state_manager.peek_below_top()
