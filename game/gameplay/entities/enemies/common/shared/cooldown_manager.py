class CooldownManager:
    def __init__(self):
        self.cooldowns = {}

    def set(self, name, duration):
        self.cooldowns[name] = duration

    def update(self, dt):
        for key in list(self.cooldowns.keys()):
            self.cooldowns[key] -= dt
            if self.cooldowns[key] <= 0:
                del self.cooldowns[key]

    def get(self, name):
        return self.cooldowns.get(name, 0)