class ProjectileSpawnRequestTracker:
    def __init__(self):
        self.requests = []

    def track(self, request):
        if request is not None:
            self.requests.append(request)
        return request

    def cancel_all(self):
        for request in self.requests:
            request.cancel()
        self.requests.clear()
