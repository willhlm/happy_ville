class LookOffsetController:
    def __init__(self, camera_manager):
        self.camera_manager = camera_manager
        self.offset = [0.0, 0.0]
        self.max_displacement = [100.0, 50.0]
        self.return_rate = 0.12

    def reset(self):
        self.offset = [0.0, 0.0]

    def update(self, dt):
        self.offset[0] += (0.0 - self.offset[0]) * self.return_rate
        self.offset[1] += (0.0 - self.offset[1]) * self.return_rate

    def handle_movement(self, value):
        if max(abs(value[0]), abs(value[1])) == 0:
            return

        self.offset[0] = max(-self.max_displacement[0], min(self.max_displacement[0], self.offset[0] - value[0]))
        self.offset[1] = max(-self.max_displacement[1], min(self.max_displacement[1], self.offset[1] - value[1]))
