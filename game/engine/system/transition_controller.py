from typing import Callable, Optional, Any

class TransitionController:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._busy = False

        self._action: Optional[Callable[[], Any]] = None
        self._on_covered: Optional[Callable[[], Any]] = None
        self._after: Optional[Callable[[], Any]] = None
        self._style = "alpha"
        self._fade_kwargs = {}

        self._fade_in_started = False

        self.game_objects.signals.subscribe("fade_covered", self._on_fade_covered)
        self.game_objects.signals.subscribe("fade_in_finished", self._on_fade_in_finished)

    @property
    def is_busy(self):
        return self._busy

    def run(self,previous_state,*,style: str = "alpha", action: Optional[Callable[[], Any]] = None, on_covered: Optional[Callable[[], Any]] = None, after: Optional[Callable[[], Any]] = None, **fade_kwargs):
        if self._busy:
            return  # or queue

        self._busy = True
        self._fade_in_started = False
        self._action = action
        self._on_covered = on_covered
        self._after = after
        self._style = style
        self._fade_kwargs = dict(fade_kwargs)

        # Optional: freeze here (input/ai/physics) if you have such a mechanism
        # self.game_objects.freeze("transition")

        # Start fade out (fade state will emit fade_covered when fully black)
        self.game_objects.game.state_manager.enter_state(
            "screen_fade",
            under_state=previous_state,
            initial_alpha=0,
            target_alpha=255,
            style=style,
            signal_name="fade_covered",
            **fade_kwargs,
        )

    def _on_fade_covered(self, **kwargs):
        if not self._busy or self._fade_in_started:
            return

        # Run blocking action while fully black
        if self._action:
            self._action()

        if self._on_covered:
            self._on_covered()

        # Start fade in
        self._fade_in_started = True
        self.game_objects.game.state_manager.enter_state(
            "screen_fade",
            initial_alpha=255,
            target_alpha=0,
            style=self._style,
            signal_name="fade_in_finished",
            **self._fade_kwargs,
        )

    def _on_fade_in_finished(self, **kwargs):
        if not self._busy or not self._fade_in_started:
            return

        # Now it's safe to "resume the world" and run post hooks
        try:
            if self._after:
                self._after()
        finally:
            self._action = None
            self._on_covered = None
            self._after = None
            self._style = "alpha"
            self._fade_kwargs = {}
            self._busy = False
            self._fade_in_started = False

            # Optional: unfreeze here
            # self.game_objects.unfreeze("transition")
