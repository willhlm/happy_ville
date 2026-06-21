class PendingSpawn:
    def __init__(
        self,
        spawn_position,
        impact_position,
        timer,
        warning_window,
        warning_interval,
        warning_callback,
        spawn_callback,
    ):
        self.spawn_position = spawn_position
        self.impact_position = impact_position
        self.timer = timer
        self.warning_window = warning_window
        self.warning_interval = warning_interval
        self.warning_callback = warning_callback
        self.spawn_callback = spawn_callback
        self.warning_timer = 0

    def update(self, dt):
        self.timer -= dt
        self.warning_timer -= dt

    def should_warn(self):
        return (
            self.warning_callback is not None
            and self.timer > 0
            and self.timer <= self.warning_window
            and self.warning_timer <= 0
        )

    def reset_warning_timer(self):
        self.warning_timer = self.warning_interval

    def should_spawn(self):
        return self.timer <= 0
