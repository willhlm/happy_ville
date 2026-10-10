from engine import constants as C

from .base import Sequence


class MapTraversalSequence(Sequence):
    """Forces a player action across a path-triggered map transition."""

    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    ACTIONS = {"idle", "run_left", "run_right", "jump", "fall"}
    def __init__(
        self,
        game_objects,
        manager,
        key,
        *,
        destination,
        spawn,
        departure_action,
        arrival_action,
        arrival_lock_time,
        wait_for_arrival_path_clear,
        previous_state,
    ):
        super().__init__(game_objects, manager, key)
        self._validate_action("departure_action", departure_action)
        self._validate_action("arrival_action", arrival_action)

        self.departure_action = departure_action
        self.arrival_action = arrival_action
        self.arrival_lock_time = max(0, int(arrival_lock_time))
        self.wait_for_arrival_path_clear = wait_for_arrival_path_clear
        self.action = departure_action
        self.phase = "departure"
        self.entry_time = 0
        self.arrival_paths = set()

        self._apply_action(self.departure_action)
        self.game_objects.map.load_map(
            previous_state,
            destination,
            spawn,
            on_loaded=self._arrive,
        )

    def update(self, dt):
        self._maintain_action()
        if self.phase != "arrival":
            return

        self.entry_time = max(0, self.entry_time - dt)
        self._finish_if_ready()

    def path_cleared(self, path):
        if self.phase != "arrival":
            return
        self.arrival_paths.discard(path)
        self._finish_if_ready()

    def _arrive(self):
        self.phase = "arrival"
        self.action = self.arrival_action
        self.entry_time = self.arrival_lock_time
        self._apply_action(self.arrival_action)
        if self.wait_for_arrival_path_clear:
            self.arrival_paths = {
                path
                for path in self.game_objects.interactables_bg
                if getattr(path, "is_path_collision", False)
                and path.hitbox.colliderect(self.game_objects.player.hitbox)
            }
        self._finish_if_ready()

    def _apply_action(self, action):
        player = self.game_objects.player
        if action == "run_left":
            self._start_run(-1)
        elif action == "run_right":
            self._start_run(1)
        elif action == "jump":
            player.currentstate.enter_state("jump")
        elif action == "fall":
            player.currentstate.enter_state("fall")
        else:
            player.currentstate.enter_state("idle")

    def _maintain_action(self):
        if self.action == "run_left":
            self._maintain_run(-1)
        elif self.action == "run_right":
            self._maintain_run(1)

    def _validate_action(self, property_name, action):
        if action not in self.ACTIONS:
            raise ValueError(f"Unknown path {property_name}: {action!r}")

    def _start_run(self, direction):
        player = self.game_objects.player
        player.dir[0] = direction
        player.acceleration[0] = C.acceleration[0]
        player.velocity[0] = direction * (C.acceleration[0] / C.friction_player[0])
        player.currentstate.enter_state("run", phase="main")

    def _maintain_run(self, direction):
        player = self.game_objects.player
        player.dir[0] = direction
        player.acceleration[0] = C.acceleration[0]
        if player.currentstate.is_in_state("idle"):
            player.currentstate.enter_state("run", phase="main")

    def _finish_if_ready(self):
        if self.entry_time == 0 and not self.arrival_paths:
            self.finish()
