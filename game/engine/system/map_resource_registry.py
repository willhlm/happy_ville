class MapResourceRegistry:
    """Owns cleanup callbacks for GPU resources that live for one loaded map."""

    def __init__(self):
        self._release_callbacks = {}

    def register(self, key, release_callback):
        self._release_callbacks[key] = release_callback

    def release_all(self):
        callbacks = tuple(self._release_callbacks.values())
        self._release_callbacks.clear()
        for release_callback in callbacks:
            release_callback()
