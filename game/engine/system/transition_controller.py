from typing import Callable, Optional, Any

class TransitionController:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._busy = False

        self._action: Optional[Callable[[], Any]] = None
        self._after: Optional[Callable[[], Any]] = None

        self._fade_in_started = False

        self.game_objects.signals.subscribe("fade_covered", self._on_fade_covered)
        self.game_objects.signals.subscribe("fade_in_finished", self._on_fade_in_finished)

    def run(self,previous_state,*,style: str = "fade_black",action: Optional[Callable[[], Any]] = None,after: Optional[Callable[[], Any]] = None,**fade_kwargs,):
        if self._busy:
            return  # or queue; up to you

        self._busy = True
        self._fade_in_started = False
        self._action = action
        self._after = after

        # Optional: freeze here (input/ai/physics) if you have such a mechanism
        # self.game_objects.freeze("transition")

        # Start fade out (fade state will emit fade_covered when fully black)
        self.game_objects.game.state_manager.enter_state("fade_out",previous_state=previous_state,style=style,**fade_kwargs)

    def _on_fade_covered(self, *args, **kwargs):
        if not self._busy or self._fade_in_started:
            return

        # Run blocking action while fully black
        if self._action:
            self._action()

        # Start fade in
        self._fade_in_started = True
        self.game_objects.game.state_manager.enter_state("fade_in")

    def _on_fade_in_finished(self, *args, **kwargs):
        if not self._busy or not self._fade_in_started:
            return

        # Now it's safe to "resume the world" and run post hooks
        try:
            if self._after:
                self._after()
        finally:
            self._action = None
            self._after = None
            self._busy = False
            self._fade_in_started = False

            # Optional: unfreeze here
            # self.game_objects.unfreeze("transition")
