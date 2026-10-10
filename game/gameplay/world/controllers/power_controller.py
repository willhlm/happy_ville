"""Generic registry for named, binary power sources."""


class PowerController:
    """Resolve power without knowing how individual sources produce it."""

    def __init__(self):
        self._sources = {}
        self._listener_adapters = {}

    def register_source(
        self,
        source_id,
        resolver,
        *,
        subscribe=None,
        unsubscribe=None,
    ):
        source_id = str(source_id).strip()
        if not source_id:
            raise ValueError("A power source needs a non-empty ID.")
        if not callable(resolver):
            raise TypeError("A power source resolver must be callable.")
        if (subscribe is None) != (unsubscribe is None):
            raise ValueError(
                "A power source must provide both subscribe and unsubscribe callbacks."
            )

        source = {
            "resolver": resolver,
            "subscribe": subscribe,
            "unsubscribe": unsubscribe,
        }
        previous = self._sources.get(source_id)
        if previous is not None:
            if previous != source:
                raise ValueError(
                    f"Power source '{source_id}' was registered more than once."
                )
            return
        self._sources[source_id] = source

    def is_registered(self, source_id):
        return source_id is None or str(source_id).strip() in self._sources

    def is_powered(self, source_id, **requirements):
        """Return the final binary state supplied by a registered provider."""
        if source_id is None:
            return True
        source_id = str(source_id).strip()
        try:
            resolver = self._sources[source_id]["resolver"]
        except KeyError as error:
            raise KeyError(f"Unknown power source '{source_id}'.") from error
        return bool(resolver(**requirements))

    def subscribe(self, source_id, listener, **requirements):
        """Subscribe to normalized ``power_source`` and ``powered`` events."""
        source_id = str(source_id).strip()
        try:
            source = self._sources[source_id]
        except KeyError as error:
            raise KeyError(f"Unknown power source '{source_id}'.") from error
        if source["subscribe"] is None:
            raise ValueError(f"Power source '{source_id}' does not publish changes.")

        key = self._listener_key(source_id, listener, requirements)
        if key in self._listener_adapters:
            return

        def adapter(**kwargs):
            listener(
                power_source=source_id,
                powered=self.is_powered(source_id, **requirements),
            )

        self._listener_adapters[key] = adapter
        source["subscribe"](adapter)

    def unsubscribe(self, source_id, listener, **requirements):
        source_id = str(source_id).strip()
        key = self._listener_key(source_id, listener, requirements)
        adapter = self._listener_adapters.pop(key, None)
        if adapter is None:
            return
        source = self._sources.get(source_id)
        if source is not None and source["unsubscribe"] is not None:
            source["unsubscribe"](adapter)

    @staticmethod
    def _listener_key(source_id, listener, requirements):
        try:
            requirement_key = tuple(sorted(requirements.items()))
            hash(requirement_key)
        except TypeError as error:
            raise TypeError("Power subscription requirements must be hashable.") from error
        return source_id, listener, requirement_key
