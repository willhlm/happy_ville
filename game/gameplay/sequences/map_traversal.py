from engine import constants as C

from .base import Sequence


class MapTraversalSequence(Sequence):
    """Forces a player action across a path-triggered map transition."""

    blocks_gameplay_input = True
    blocks_gameplay_movement = True

    ACTIONS = {"idle", "run_left", "run_right", "jump", "fall"}
    # Keep the forced action visible after the destination map is ready.
    # Collision paths can extend this further until the player leaves them.
    MIN_ENTRY_TIME = 45

    def __init__(self, game_objects, manager, key, *, destination, spawn, entry_action,
                 previous_state):
        super().__init__(game_objects, manager, key)
        if entry_action not in self.ACTIONS:
            raise ValueError(f"Unknown path entry_action: {entry_action!r}")

        self.entry_action = entry_action
        self.phase = "departure"
        self.entry_time = 0
        self.arrival_paths = set()

        self._apply_action()
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
        self.entry_time = self.MIN_ENTRY_TIME
        self._apply_action()
        self.arrival_paths = {
            path
            for path in self.game_objects.interactables
            if getattr(path, "is_path_collision", False)
            and path.hitbox.colliderect(self.game_objects.player.hitbox)
        }
        self._finish_if_ready()

    def _apply_action(self):
        player = self.game_objects.player
        if self.entry_action == "run_left":
            self._start_run(-1)
        elif self.entry_action == "run_right":
            self._start_run(1)
        elif self.entry_action == "jump":
            player.currentstate.enter_state("jump")
        elif self.entry_action == "fall":
            player.currentstate.enter_state("fall")
        else:
            player.currentstate.enter_state("idle")

    def _maintain_action(self):
        if self.entry_action == "run_left":
            self._maintain_run(-1)
        elif self.entry_action == "run_right":
            self._maintain_run(1)

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
