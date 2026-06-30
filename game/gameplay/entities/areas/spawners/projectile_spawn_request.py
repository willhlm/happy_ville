class ProjectileSpawnRequest:
    def __init__(self):
        self.entries = []

    def add_entry(self, spawner, request_id):
        self.entries.append((spawner, request_id))

    def cancel(self):
        for spawner, request_id in self.entries:
            spawner.cancel_pending_spawns(request_id)
        self.entries.clear()
