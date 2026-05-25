class ItemLifetimeComponent:
    def __init__(self, item, lifetime):
        self.item = item
        self.lifetime = lifetime

    def update(self, dt):
        if self.item.consumed:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.item.start_fade()
