class StatusComponent:
    def __init__(self, entity, registry=None):
        self.entity = entity
        self.registry = registry or {}
        self.statuses = {}

    def register(self, name, factory):
        self.registry[name] = factory

    def get(self, name):
        if name not in self.statuses and name in self.registry:
            self.statuses[name] = self.registry[name](self.entity)
        return self.statuses.get(name)

    def activate(self, name, *args, **kwargs):
        status = self.get(name)
        if status:
            status.activate(*args, **kwargs)
        return status

    def deactivate(self, name):
        status = self.get(name)
        if status:
            status.deactivate()
        return status

    def has(self, name):
        status = self.statuses.get(name)
        return bool(status and status.active)

    def update(self, dt):
        for status in self.statuses.values():
            status.update(dt)
