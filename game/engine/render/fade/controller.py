class FadeController:
    def __init__(self, value=0.0, *, min_value=0.0, max_value=255.0, on_complete=None):
        self.value = float(value)
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.on_complete = on_complete
        self._completed = False
        self.clamp()

    def clamp(self):
        self.value = max(self.min_value, min(self.max_value, self.value))
        return self.value

    def set(self, value):
        self.value = float(value)
        return self.clamp()

    def step(self, delta):
        self.value += delta
        return self.clamp()

    def step_linear(self, dt, speed):
        return self.step(dt * speed)

    def decay(self, rate):
        self.value *= rate
        return self.clamp()

    def approach(self, target, speed, dt, *, dt_scale=0.01):
        if speed <= 0:
            return self.set(target)

        step = min(1.0, speed * dt * dt_scale)
        self.value += (target - self.value) * step
        return self.clamp()

    def is_below(self, threshold):
        return self.value < threshold

    def complete(self):
        if self._completed:
            return

        self._completed = True
        if self.on_complete:
            self.on_complete()
