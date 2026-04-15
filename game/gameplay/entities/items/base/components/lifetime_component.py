class ItemLifetimeComponent:
    def __init__(self, item, lifetime):
        self.item = item
        self.lifetime = lifetime

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.item.kill()

