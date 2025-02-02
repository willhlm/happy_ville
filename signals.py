class Signals():
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, listener):
        """Register a listener for a specific event."""
        self.listeners.setdefault(event_type, []).append(listener)

    def emit(self, event_type, **kwargs):
        """Trigger all listeners for a specific event."""
        for listener in self.listeners.get(event_type, []):
            listener(**kwargs)

    def unsubscribe(self, event_type, listener):
        """Remove a listener from an event type."""
        if event_type in self.listeners:
            self.listeners[event_type].remove(listener)
            if not self.listeners[event_type]:  # Remove event type if no listeners remain
                del self.listeners[event_type]