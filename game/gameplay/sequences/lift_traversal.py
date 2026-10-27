"""Map handoff for a player riding a cross-map lift."""

from .base import Sequence


class LiftTraversalSequence(Sequence):
    """Load the destination map, then place the player on its matching lift."""

    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    def __init__(self, game_objects, manager, key, *, destination,
                 destination_lift_id, previous_state):
        super().__init__(game_objects, manager, key)
        self.destination_lift_id = str(destination_lift_id)
        self.loaded = False
        temporary_spawn = tuple(self.game_objects.player.rect.topleft)
        self.game_objects.map.load_map(
            previous_state,
            destination,
            temporary_spawn,
            on_loaded=self._arrive,
        )

    def update(self, _dt):
        if self.loaded and not self.game_objects.transition.is_busy:
            self.finish()

    def _arrive(self):
        lift = next(
            (
                platform for platform in self.game_objects.platforms
                if getattr(platform, "lift_id", None) == self.destination_lift_id
            ),
            None,
        )
        if lift is None:
            raise ValueError(
                f"Destination lift {self.destination_lift_id!r} was not found "
                f"in {self.game_objects.map.biome_room_name!r}"
            )
        lift.place_at_station(1)
        player = self.game_objects.player
        # EntityBody.set_pos expects the sprite centre.  Put that centre over
        # the car's centre while keeping the sprite's feet on its top edge.
        player.body.set_pos((lift.rect.centerx, lift.rect.top - player.rect.height / 2))
        player.reset_movement()
        lift.request_station(0)
        self.loaded = True
