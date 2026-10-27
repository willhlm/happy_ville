from gameplay.sequences.base import Sequence


class SejteTravelSequence(Sequence):
    """Travel between installed Sejte save points under a screen transition."""

    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    def __init__(
        self,
        game_objects,
        manager,
        key,
        *,
        destination,
        spawn,
        previous_state,
    ):
        super().__init__(game_objects, manager, key)
        self.destination = destination
        self.spawn = list(spawn)

        self.game_objects.player.currentstate.enter_state(
            'sejte_travel',
            phase='depart',
        )
        self.game_objects.transition.run(
            previous_state=previous_state,
            style='alpha',
            action=self._load_destination,
            on_covered=self._arrive,
            after=self._finish,
            fade_length=40,
        )

    def _load_destination(self):
        self.game_objects.map.load_now(self.destination, self.spawn)

    def _arrive(self):
        self.game_objects.player.currentstate.enter_state(
            'sejte_travel',
            phase='arrive',
        )

    def _finish(self):
        self.game_objects.player.currentstate.handle_input('finish')
        self.finish()

    def cleanup(self):
        if self.game_objects.player.currentstate.is_in_state('sejte_travel'):
            self.game_objects.player.currentstate.handle_input('finish')
